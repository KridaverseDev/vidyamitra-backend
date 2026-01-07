from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from silicon.questions.models import FavoriteQuestion, Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["question", "course", "marks", "validated", "is_favorite"]
    actions = ["mark_as_favorite", "remove_as_favorite"]

    def is_favorite(self, obj):
        """Check if the question is marked as a favorite."""
        return FavoriteQuestion.objects.filter(question=obj).exists()

    is_favorite.boolean = True
    is_favorite.short_description = "Is Favorite"

    def mark_as_favorite(self, request, queryset):
        """Custom action to mark selected questions as favorite."""
        marked_count = 0
        for question in queryset:
            if not question.validated:
                self.message_user(
                    request,
                    f"Cannot mark unvalidated question '{question}' as favorite.",
                    level="error",
                )
                continue

            try:
                _, created = FavoriteQuestion.objects.get_or_create(question=question)
                if created:
                    marked_count += 1
                else:
                    self.message_user(
                        request,
                        f"Question '{question}' is already a favorite.",
                        level="warning",
                    )
            except ObjectDoesNotExist:
                self.message_user(
                    request, f"Question {question} not found.", level="error"
                )
            except ValidationError as e:
                self.message_user(request, f"Validation error: {str(e)}", level="error")
            except Exception as e:
                self.message_user(request, f"Error: {str(e)}", level="error")

        if marked_count > 0:
            self.message_user(request, f"Marked {marked_count} questions as favorite.")

    mark_as_favorite.short_description = "Mark selected questions as favorite"

    def remove_as_favorite(self, request, queryset):
        """Custom action to remove selected questions from favorites."""
        removed_count = 0
        for question in queryset:
            try:
                favorite = FavoriteQuestion.objects.get(question=question)
                favorite.delete()
                removed_count += 1
            except FavoriteQuestion.DoesNotExist:
                self.message_user(
                    request,
                    f"Question '{question}' is not marked as favorite.",
                    level="warning",
                )
            except Exception as e:
                self.message_user(request, f"Error: {str(e)}", level="error")

        if removed_count > 0:
            self.message_user(
                request, f"Removed {removed_count} questions from favorites."
            )

    remove_as_favorite.short_description = "Remove selected questions from favorites"


@admin.register(FavoriteQuestion)
class FavoriteQuestionAdmin(admin.ModelAdmin):
    list_display = ["question", "created"]
    list_filter = ["created"]
    search_fields = ["question__question"]
    actions = ["remove_favorite"]

    def remove_as_favorite(self, request, queryset):
        """Custom action to remove selected favorites."""
        removed_count = 0
        for favorite in queryset:
            try:
                # Delete the favorite entry
                favorite.delete()
                removed_count += 1
            except Exception as e:
                self.message_user(request, f"Error: {str(e)}", level="error")

        if removed_count > 0:
            self.message_user(request, f"Removed {removed_count} favorites.")

    remove_as_favorite.short_description = "Remove selected from favorites"
