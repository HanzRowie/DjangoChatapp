from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    get_chat_messages,
    send_message,
    get_or_create_private_chatroom,
    chat_test_view,
    get_current_user,
    all_users
)

urlpatterns = [
    # 🔐 Auth endpoints
    path('RegisterView/', RegisterView.as_view(), name='RegisterView'),
    path('LoginView/', LoginView.as_view(), name='LoginView'),

    # 💬 Chat message APIs
    path('api/chatroom/<str:chatroom_name>/messages/', get_chat_messages, name='get-messages'),
    path('api/chatroom/<str:chatroom_name>/send/', send_message, name='send-message'),

    # 🏠 Chatroom management
    # path('api/chatroom/private/<str:username>/', get_or_create_private_chatroom, name='private-chatroom'),
    path('get_or_create_private_chatroom/<str:username>/', get_or_create_private_chatroom),
     path('test-chat/', chat_test_view),
    path('api/user/', get_current_user),
    path('all_users/', all_users),

]
