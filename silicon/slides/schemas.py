from ninja import ModelSchema
from ninja.schema import Schema

from silicon.slides import models


class GeneratePPTIn(Schema):
    """Schema for accepting input for creating a presentation."""

    count: int
    title: str
    query: str


class PresentationOut(ModelSchema):
    """Schema for displaying the Presentation object."""

    class Meta:
        model = models.Presentation
        fields = "__all__"
        exclude = ["course"]


class SlideOut(ModelSchema):
    """Schema for displaying a Slide object."""

    class Meta:
        model = models.Slides
        fields = "__all__"
        exclude = ["presentation"]


class GetPresentation(Schema):
    """Schema for displaying presentation along with the slides."""

    presentation: PresentationOut
    slides: list[SlideOut]


class SlideIn(ModelSchema):
    """Schema for taking input for updating the slides."""

    class Meta:
        model = models.Slides
        fields = ["title", "content"]
        fields_optional = "__all__"


class FavoriteOut(ModelSchema):
    """Schema to display the favorites."""

    class Meta:
        model = models.Favorite
        fields = "__all__"
        exclude = ["id"]
