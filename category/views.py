from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Product, Category, Comment
from orders.forms import CartAddForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CommentReplyForm, CommentCreateForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


# Create your views here.

class ProductView(View):
    template_name = 'category/index.html'

    def get(self, request, category_slug=None):
        products = Product.objects.filter(available=True)
        categories = Category.objects.filter(is_sub=False)
        if category_slug:
            category = Category.objects.get(slug=category_slug)
            products = products.filter(category=category)
        return render(request, self.template_name, {'products': products, 'categories': categories})


class ProductDetailView(View):
    template_name = 'category/detail.html'
    form_class = CommentCreateForm
    form_class_reply = CommentReplyForm

    def setup(self, request, *args, **kwargs):
        self.post_instead = get_object_or_404(Product, slug=kwargs['slug'])
        return super().setup(request, *args, **kwargs)

    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        comments = self.post_instead.pcomments.filter(is_reply=False)
        form = CartAddForm
        return render(request, self.template_name,
                      {'product': product, 'form': form, 'comments': comments, 'form_comment': self.form_class,
                       'reply_form': self.form_class_reply})

    @method_decorator(login_required())
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_commend = form.save(commit=False)
            new_commend.user = request.user
            new_commend.post = self.post_instead
            new_commend.save()
            messages.success(request, 'your comment added for this form (language level up)', 'success')
            return redirect('category:product', self.post_instead.slug)


class PostAddReplyView(LoginRequiredMixin, View):
    form_class = CommentReplyForm

    def post(self, request, post_id, comment_id):
        post = get_object_or_404(Product, pk=post_id)
        comment = get_object_or_404(Comment, pk=comment_id)
        form = self.form_class(request.POST)
        if form.is_valid():
            new_reply = form.save(commit=False)
            new_reply.user = request.user
            new_reply.post = post
            new_reply.reply = comment
            new_reply.is_reply = True
            new_reply.save()
            messages.success(request, 'your reply been added :)', 'success')
        return redirect('category:product', post.slug)
