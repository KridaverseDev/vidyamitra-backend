import requests
from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError
from ninja_extra import api_controller, route
from ninja_extra.pagination import (
    PageNumberPaginationExtra,
    PaginatedResponseSchema,
    paginate,
)

from silicon._sdk import authentication, permissions
from silicon.slides import schemas
from silicon.slides.models import Favorite, Presentation, Slides
from silicon.slides.services import PresentationService


# class based definition
@api_controller(
    "v1/presentations",
    tags=["Presentation"],
    auth=[authentication.token_auth],
    permissions=[permissions.IsAuthenticated],
)
class PresentationAPI:
    def __init__(self):
        # Default service for methods that don't need user-specific API keys
        self.ppt = PresentationService()
    
    def _get_service(self, user=None):
        """Get PresentationService instance with user context for API key resolution."""
        return PresentationService(user=user)

    @route.get(
        "",
        url_name="list-presentations",
        response=PaginatedResponseSchema[schemas.PresentationOut],
    )
    @paginate(PageNumberPaginationExtra, page_size=10)
    def list_presentations(self):
        """List all the presentations."""
        try:
            return Presentation.objects.all()
        except Exception as e:
            raise HttpError(400, str(e))

    @route.get(
        "/favorites",
        url_name="list-favorites",
        response=PaginatedResponseSchema[schemas.FavoriteOut],
    )
    @paginate(PageNumberPaginationExtra, page_size=10)
    def list_favorites(self, request):
        """List the marked favorites."""
        return Favorite.objects.filter(user=request.auth)

    @route.get("/{id}", url_name="get-presentation")
    def get_presentations(self, id: int, export: bool = False):
        """
        Get the presentation.
        
        If export=True, returns a downloadable PPTX file.
        Otherwise, returns presentation data with slides (JSON).
        """
        if export:
            # Export and return file for download
            try:
                result = self.ppt.export_presentation(id)
                file_url = result.get("file_path")
                filename = result.get("filename", "presentation.pptx")
                
                if not file_url:
                    raise HttpError(500, "Failed to generate presentation file")
                
                # Download the file from S3 URL
                response = requests.get(file_url)
                if response.status_code != 200:
                    raise HttpError(500, f"Failed to download generated file from S3: {response.status_code}")
                
                # Create HTTP response with file
                http_response = HttpResponse(
                    response.content,
                    content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
                http_response["Content-Disposition"] = f'attachment; filename="{filename}"'
                http_response["Content-Length"] = len(response.content)
                
                return http_response
                
            except requests.RequestException as e:
                raise HttpError(500, f"Failed to download file: {str(e)}")
            except Exception as e:
                raise HttpError(500, f"Error exporting presentation: {str(e)}")
        else:
            # Return presentation data
            return self.ppt.get_presentation(id)

    @route.post("/{document_id}/", url_name="generate-presentation")
    def generate_presentation(
        self,
        request,
        document_id: int,
        payload: schemas.GeneratePPTIn,
    ):
        """Generate a presentation based on document id."""
        service = self._get_service(user=request.auth)  # Use user-specific service
        return service.generate_presentation(
            document_id=document_id, payload=payload, request=request
        )

    @route.delete("/{id}", url_name="delete-presentations", response={204: None})
    def delete_presentation(self, id: int):
        """Delete a presentation."""
        self.ppt.delete_presentation(id)

    @route.post("/{id}/favorites", url_name="mark-favorite")
    def mark_favorite(self, request, id: int):
        """Mark a presentation as favorite."""
        return self.ppt.favorite_presentation(request=request, id=id)

    @route.delete("/{id}/favorites", url_name="delete-favorite", response={204: None})
    def delete_favorite(self, request, id: int):
        """Delete a presentation."""
        ppt = get_object_or_404(Presentation, pk=id)
        fav = get_object_or_404(Favorite, ppt=ppt, user=request.auth)
        fav.delete()

    @route.put("/slide/{id}", url_name="update slide", response={204: None})
    def update_slide(self, id: int, payload: schemas.SlideIn):
        """Update a slide."""
        return self.ppt.update_slide(slide_id=id, payload=payload)

    @route.delete("/slide/{id}", url_name="delete-slide", response={204: None})
    def delete_slide(self, id: int):
        """Delete a slide object."""
        slide = get_object_or_404(Slides, pk=id)
        slide.delete()
