from accounts.common_imports import *
from blog.models import *
from blog.serializer import *

'''
Blogs List
'''
class BlogsListAPI(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Blogs"],
        operation_id="blogs_list",
        operation_description="Blogs Listing",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request, *args, **kwargs):
        blogs=Blogs.objects.filter(status=ACTIVE_BLOG).order_by('-created_on')
        start,end,meta_data=GetPagesData(request.query_params.get('page') if request.query_params.get('page') else None,blogs)
        data=BlogSerializer(blogs[start:end],many=True,context={"request":request}).data
        return Response({"data":data,"meta_data":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)

'''
Blog Details
'''
class ViewBlogAPI(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        tags=["Blogs"],
        operation_id="blog_details",
        operation_description="ViewBlogAPI",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request, *args, **kwargs):
        try:
            blog=Blogs.objects.get(id=request.query_params.get('id'))
        except:
            return Response({"message":"Blog does not exists!","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        data=BlogSerializer(blog,context={"request":request}).data
        return Response({"data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
