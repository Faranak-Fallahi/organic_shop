from .models import Post
from rest_framework import serializers

class PostListSerializer(serializers.ModelSerializer):
    comments_count = serializers.IntegerField(read_only=True)
    summary = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 
            'title', 
            'slug',
            'summary', 
            'created_at', 
            'updated_at', 
            'published', 
            'image',
            'comments_count',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
        
    def get_summary(self, obj):
        if obj.content:
            return obj.content[:150] + '...' if len(obj.content) > 150 else obj.content
        return 


class PostDetailSerializer(serializers.ModelSerializer):
    comments_count = serializers.IntegerField(read_only=True)
    

    class Meta:
        model = Post
        fields = [
            'id', 
            'title', 
            'slug', 
            'content', 
            'comments_count',
            'created_at', 
            'updated_at', 
            'published', 
            'image'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    