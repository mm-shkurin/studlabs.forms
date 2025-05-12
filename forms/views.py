from rest_framework import generics, permissions
from .models import Form, Response
from .serializers import *
from .permissions import IsOwnerOrReadOnly
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Form
from .serializers import FormCreateSerializer, FormSerializer
class FormCreateView(generics.CreateAPIView):
    serializer_class = FormCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Создать новую форму",
        operation_description="Создает форму с вопросами и вариантами ответов",
        request_body=FormCreateSerializer,
        responses={
            201: openapi.Response('Форма создана', FormSerializer),
            400: "Неверные данные",
            401: "Не авторизован"
        },
        security=[{"Bearer": []}]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
class FormListView(generics.ListAPIView):
    serializer_class = FormSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Список форм пользователя",
        operation_description="Возвращает все формы, созданные текущим пользователем.",
        manual_parameters=[
            openapi.Parameter(
                'search', openapi.IN_QUERY,
                description="Поиск по названию формы",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: FormSerializer(many=True),
            401: "Не авторизован"
        },
        security=[{"Bearer": []}]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = Form.objects.filter(owner=self.request.user)
        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
        return queryset.prefetch_related('questions__options')
class FormDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Form.objects.all().prefetch_related('questions__options')
    serializer_class = FormSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'pk'  # Явно указываем поле для поиска

    @swagger_auto_schema(
        operation_summary="Получить детали формы",
        manual_parameters=[
            openapi.Parameter(
                'pk', openapi.IN_PATH,
                description="ID формы",
                type=openapi.TYPE_STRING,
                example="OcIiYEYl9Z"
            )
        ],
        responses={
            200: FormSerializer,
            401: openapi.Response("Не авторизован"),
            403: openapi.Response("Нет прав доступа"),
            404: openapi.Response("Форма не найдена")
        },
        security=[{"Bearer": []}]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Полное обновление формы",
        operation_description="Обновляет все поля формы, включая вопросы и варианты ответов",
        request_body=FormSerializer,
        responses={
            200: FormSerializer,
            400: openapi.Response("Неверные данные"),
            403: openapi.Response("Нет прав доступа")
        },
        security=[{"Bearer": []}]
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Частичное обновление формы",
        operation_description="Обновляет только указанные поля формы",
        request_body=FormSerializer,
        responses={
            200: FormSerializer,
            400: openapi.Response("Неверные данные"),
            403: openapi.Response("Нет прав доступа")
        },
        security=[{"Bearer": []}]
    )
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удалить форму",
        operation_description="Удаляет форму и все связанные вопросы и ответы",
        responses={
            204: "Форма удалена",
            403: "Нет прав доступа",
            404: "Форма не найдена"
        },
        security=[{"Bearer": []}]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

class ResponseCreateView(generics.CreateAPIView):
    serializer_class = ResponseSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Отправить ответ на форму",
        operation_description="Создает новый ответ на указанную форму. Доступно без авторизации.",
        manual_parameters=[
            openapi.Parameter(
                'form_id', openapi.IN_PATH,
                description="ID формы",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=ResponseSerializer,
        responses={
            201: "Ответ успешно сохранен",
            400: "Неверные данные ответа",
            404: "Форма не найдена"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def get_form_instance(self):
        form_id = self.kwargs.get('form_id')
        return generics.get_object_or_404(Form, id=form_id)
    
    def perform_create(self, serializer):
        form = self.get_form_instance()
        serializer.save(form=form)

class FormStatsView(generics.RetrieveAPIView):
    serializer_class = FormStatsSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'id'

    @swagger_auto_schema(
        operation_summary="Статистика по форме",
        operation_description="Возвращает статистику ответов для указанной формы. Только для владельца формы.",
        manual_parameters=[
            openapi.Parameter(
                'id', openapi.IN_PATH,
                description="ID формы",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'Authorization', openapi.IN_HEADER,
                description="JWT токен: Bearer <token>",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: FormStatsSerializer,
            401: "Не авторизован",
            403: "Нет прав доступа",
            404: "Форма не найдена"
        },
        security=[{"Bearer": []}]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        return Form.objects.all()