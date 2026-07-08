from rest_framework import serializers
from .models import PostComment, ProductComment


class PostCommentReplySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = PostComment
        fields = ['id', 'user', 'body', 'created_at']
        read_only_fields = fields


class PostCommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    replies = PostCommentReplySerializer(many=True, read_only=True)

    class Meta:
        model = PostComment
        fields = [
            'id',
            'user',
            'post',
            'parent',
            'body',
            'is_active',
            'created_at',
            'updated_at',
            'replies',
        ]
        read_only_fields = ['id', 'user', 'is_active', 'created_at', 'updated_at', 'replies']


class ProductCommentReplySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ProductComment
        fields = ['id', 'user', 'body', 'created_at']
        read_only_fields = fields


class ProductCommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    replies = ProductCommentReplySerializer(many=True, read_only=True)

    class Meta:
        model = ProductComment
        fields = [
            'id',
            'user',
            'product',
            'parent',
            'body',
            'is_active',
            'created_at',
            'updated_at',
            'replies',
        ]
        read_only_fields = ['id', 'user', 'is_active', 'created_at', 'updated_at', 'replies']
