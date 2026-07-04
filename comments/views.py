from .models import PostComment
from .models import ProductComment
from blog.models import Post
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from store.models import Product




@login_required
def add_post_comment(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if request.method == "POST":
        body = request.POST.get("body")
        parent_id = request.POST.get("parent_id")

        parent = None
        if parent_id:
            parent = get_object_or_404(PostComment, id=parent_id)

        PostComment.objects.create(
            user=request.user,
            post=post,
            body=body,
            parent=parent,
        )

        messages.success(request, "کامنت شما ثبت شد ✅")
        return redirect("blog:post_detail", slug=post.slug)

    return redirect("blog:post_detail", slug=post.slug)


@login_required
def delete_post_comment(request, comment_id):
    comment = get_object_or_404(PostComment, id=comment_id)
    
    # بررسی امنیتی: فقط خودِ نویسنده کامنت بتواند آن را حذف کند
    if comment.user == request.user:
        comment.delete()
        messages.success(request, "کامنت شما با موفقیت حذف شد ✅")
    else:
        messages.error(request, "شما اجازه حذف این کامنت را ندارید ❌")
        
    return redirect("blog:post_detail", slug=comment.post.slug)


@login_required
def edit_post_comment(request, comment_id):
    comment = get_object_or_404(PostComment, id=comment_id)

    if comment.user != request.user:
        messages.error(request, "اجازه ویرایش این کامنت را ندارید ❌")
        return redirect("blog:post_detail", slug=comment.post.slug)

    if request.method == "POST":
        comment.body = request.POST.get("body")
        comment.save()
        messages.success(request, "کامنت شما ویرایش شد ✅")
        return redirect("blog:post_detail", slug=comment.post.slug)

    return render(request, "comments/edit_comment.html", {
        "comment": comment,
        "back_url": comment.post.get_absolute_url() if hasattr(comment.post, "get_absolute_url") else f"/blog/{comment.post.slug}/"
    })


@login_required
def add_product_comment(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.method == "POST":
        body = request.POST.get("body")
        parent_id = request.POST.get("parent_id")

        parent = None
        if parent_id:
            parent = get_object_or_404(ProductComment, id=parent_id)

        ProductComment.objects.create(
            user=request.user,
            product=product,
            body=body,
            parent=parent,
        )

        messages.success(request, "کامنت شما ثبت شد")
        return redirect("store:product_detail", slug=product.slug)

    return redirect("store:product_detail", slug=product.slug)


@login_required
def delete_product_comment(request, comment_id):
    comment = get_object_or_404(ProductComment, id=comment_id)

    if comment.user == request.user:
        comment.delete()
        messages.success(request, "کامنت با موفقیت حذف شد")
    else:
        messages.error(request, "شما اجازه حذف این کامنت را ندارید")

    return redirect("store:product_detail", slug=comment.product.slug)


@login_required
def edit_product_comment(request, comment_id):
    comment = get_object_or_404(ProductComment, id=comment_id)

    if comment.user != request.user:
        messages.error(request, "اجازه ویرایش این کامنت را ندارید")
        return redirect("store:product_detail", slug=comment.product.slug)

    if request.method == "POST":
        comment.body = request.POST.get("body")
        comment.save()
        messages.success(request, "کامنت با موفقیت ویرایش شد")
        return redirect("store:product_detail", slug=comment.product.slug)

    return render(request, "comments/edit_comment.html", {
        "comment": comment,
        "back_url": f"/store/{comment.product.slug}/"
    })
