from rest_framework import generics, permissions
from .models import Form, Response
from .serializers import *
from .permissions import IsOwnerOrReadOnly

class FormCreateView(generics.CreateAPIView):
    serializer_class = FormCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save()

class FormListView(generics.ListAPIView):
    serializer_class = FormSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Form.objects.filter(owner=self.request.user)\
               .prefetch_related('questions__options')

class FormDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Form.objects.all().prefetch_related('questions__options')
    serializer_class = FormSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

class ResponseCreateView(generics.CreateAPIView):
    serializer_class = ResponseSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_form_instance(self):
   
        form_id = self.kwargs.get('form_id')
        return generics.get_object_or_404(Form, id=form_id)
    
    def perform_create(self, serializer):
        form = self.get_form_instance()
        serializer.save(form=form)

class FormStatsView(generics.RetrieveAPIView):
    serializer_class = FormStatsSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        return Form.objects.filter(owner=self.request.user)