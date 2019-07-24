from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import (
    Tag, Post, Comment, Reply, Rating, Bookmark, Archive
    )

class View(APIView):
    def get(self, request, slug):
        try:
            post = Post.objects.get(slug=slug)


class Create(APIView):
    def post(self, request):

class Delete(APIView):
    def post(self, request):

class Update(APIView):
    def post(self, request):

class Rate(APIView):
    def post(self, request):

class Comment(APIView):
    def post(self, request):

class Reply(self, request):
    def post(self, request):

class Bookmark(APIView):
    def post(self, request):

class Archive(APIView):
    def post(self, request):

