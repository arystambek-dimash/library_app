from rest_framework import viewsets, status, mixins, exceptions, filters
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.books.models import Book, Comment, Rating
from api.books.serializers import BookSerializer, BookViewSerializer, \
    CommentSerializer, RatingSerializer, CommentChildSerializer
from .permissions import IsOwnerOrReadOnly


class MyBooksViewSet(mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    actions = ['create', 'update', 'partial_update', 'destroy']

    def get_serializer_class(self):
        if self.action == 'list':
            return BookViewSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        queryset = Book.objects.filter(user=request.user).all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BooksViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter]

    def get_queryset(self):
        queryset = Book.objects.filter(is_private=False).all()
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return BookViewSerializer
        return self.serializer_class


class CommentViewSet(mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = Comment.objects.all().order_by('-commented_at')
    serializer_class = CommentSerializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def list(self, request, *args, **kwargs):
        queryset = Comment.objects.filter(parent=None)
        serializer = CommentSerializer(queryset, many=True)
        data = serializer.data

        return Response(data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        try:
            book = Book.objects.get(pk=self.kwargs['book_id'])
            serializer.save(book=book, user=self.request.user)
        except Book.DoesNotExist:
            return Response("Book not found", status=status.HTTP_400_BAD_REQUEST)

    def get_permissions(self):
        if self.request.method in ["POST"]:
            return [IsAuthenticated()]
        elif self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAuthenticated(), IsOwnerOrReadOnly()]
        return []

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return CommentSerializer
        elif self.action == 'create':
            return CommentChildSerializer
        return CommentSerializer


class RatingViewSet(mixins.CreateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        try:
            book = get_object_or_404(Book, pk=self.kwargs['book_id'])
            if book.user == self.request.user:
                raise exceptions.PermissionDenied("You cannot rate this book")
            rating = Rating.objects.filter(book=book, user=self.request.user).first()
            if rating:
                rating.delete()
            serializer.save(user=self.request.user, book=book)
        except Book.DoesNotExist:
            return Response("Book not found", status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        try:
            book = get_object_or_404(Book, pk=self.kwargs['book_id'])
            rating = Rating.objects.get(Rating, book=book, user=self.request.user)
            rating.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Rating.DoesNotExist:
            return Response("No review found", status=status.HTTP_400_BAD_REQUEST)
