from accounts.utils import *
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializer import *
from .models import *


class UserChatsList(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Chat API's"],
        operation_id="User Chats List",
        operation_description="User Chats List",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('search', openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ],
    )
    def get(self, request, *args, **kwargs):
        chats = Chatting.objects.filter(Q(sender=request.user)|Q(receiver=request.user)).order_by("-updated_on")
        if request.query_params.get('search'):
            chats = chats.filter(Q(sender__full_name__icontains=request.query_params.get('search'))|Q(receiver__full_name__icontains=request.query_params.get('search')))
        start,end,meta_data = GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None, chats)
        data = UserChatsListSerializer(chats[start : end],many=True,context = {"request":request}).data
        return Response({"data":data,"meta":meta_data,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)
    

class SendMessage(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Chat API's"],
        operation_id="Send Message",
        operation_description="Send Message",
        manual_parameters=[
            openapi.Parameter('message', openapi.IN_FORM, type=openapi.TYPE_STRING),
            # openapi.Parameter('message_file', openapi.IN_FORM, type=openapi.TYPE_FILE), 
            openapi.Parameter('receiver_id', openapi.IN_FORM, type=openapi.TYPE_STRING), 
        ],
    )

    def post(self, request, *args, **kwargs):
        try:
            receiver = User.objects.get(id=request.data.get('receiver_id'))
        except:
            return Response({"message":"Please enter valid receiver user id","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if receiver == request.user:
            return Response({"message":"Sorry! You can not message to yourself!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not (request.data.get('message') or request.FILES.get('message_file')):
            return Response({"message":"Please enter valid message","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        sender = request.user
      
        try:
            chating = Chatting.objects.get(Q(sender=sender, receiver=receiver)|Q(sender=receiver, receiver=sender))
        except:
            chating = Chatting.objects.create(sender=sender, receiver=receiver)
        
        message = Message.objects.create(
            sender = sender,
            receiver = receiver,
            message = request.data.get('message') if request.data.get('message') else None,
            message_file = request.FILES.get('message_file') if request.FILES.get('message_file') else None,
            chat = chating
        ) 
        chating.updated_on = datetime.now()
        chating.save()
        data = MessageSerializer(message,context = {"request":request}).data
        return Response({"messages":data,"message":"Message sent successfully!"},status=status.HTTP_200_OK)
    

class MessageWindowAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Chat API's"],
        operation_id="Message Window",
        operation_description="Message Window",
        manual_parameters=[
            openapi.Parameter('receiver_id', openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_STRING), 
        ],
    )
    def post(self, request, *args, **kwargs):
        try:
            receiver = User.objects.get(id=request.data.get('receiver_id'))
        except:
            return Response({"message":"Please enter valid receiver user id","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        sender = request.user
        try:
            chating = Chatting.objects.get(Q(sender=sender, receiver=receiver)|Q(sender=receiver, receiver=sender))
        except:
            chating = None
        other_user = {
            "id":receiver.id,
            "full_name":receiver.full_name,
            "profile_pic":request.build_absolute_uri(receiver.profile_pic.url) if receiver.profile_pic else "",
        }
        if chating:
            messages = Message.objects.filter(Q(sender=sender)|Q(receiver=sender, seen=True),chat=chating).exclude(deleted_by=request.user).order_by('-created_on')
            start,end,meta_data = GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None, messages)
            data = MessageSerializer(messages.order_by('-created_on')[start : end],many=True,context = {"request":request}).data
        
            return Response({"chat_id":chating.id,"other_user":other_user,"data":data,"meta":meta_data,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)
        else:
            return Response({"other_user":other_user,"chat_muted":False,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)



class LoadMessageAPI(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Chat API's"],
        operation_id="Load Messages",
        operation_description="Load Messages",
        manual_parameters=[
            openapi.Parameter('receiver_id', openapi.IN_FORM, type=openapi.TYPE_STRING),
        ],
    )

    def post(self, request, *args, **kwargs):
        try:
            receiver = User.objects.get(id=request.data.get('receiver_id'))
        except:
            return Response({"message":"Please enter valid receiver user id","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        sender = request.user
        try:
            chating = Chatting.objects.get(Q(sender=sender, receiver=receiver)|Q(sender=receiver, receiver=sender))
        except:
            chating = None
        if chating:
            messages = Message.objects.filter(chat=chating,receiver=sender, seen=False).exclude(deleted_by=sender).order_by('created_on')
            data = MessageSerializer(messages,many=True,context={"request":request}).data
            messages.update(seen=True)
            return Response({"data":data,"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)
        else:
            return Response({"data":[],"status": status.HTTP_200_OK}, status = status.HTTP_200_OK)