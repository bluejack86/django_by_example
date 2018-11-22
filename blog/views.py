from .models import Post, Comment
from django.views import generic
from .forms import EmailPostForm, CommentForm
from django.shortcuts import get_object_or_404, render
from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from taggit.models import Tag
from django.db.models import Count


class ListView(generic.ListView):
    queryset = Post.objects.filter(status='published')
    paginate_by = 3


# default:
# context = {
#                 'paginator': paginator,
#                 'page_obj': page,
#                 'is_paginated': is_paginated,
#                 'object_list': queryset
#             }
# template_name = '<app name>/<model name>_list.html'


def post_list(request, tag_slug=None):
    posts = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags__in=[tag])
    paginator = Paginator(posts, 3)
    page_id = request.GET.get('page')
    try:
        page = paginator.page(page_id)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    context = {'object_list': page, 'page_obj': page, 'tag': tag}
    return render(request, 'blog/post_list.html', context=context)


def post_detail(request, pk):
    post = get_object_or_404(Post, id=pk)
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_tags = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_tags.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    context = {'post': post, 'comments': comments, 'new_comment': new_comment, 'comment_form': comment_form,
               'similar_posts': similar_posts}
    return render(request, 'blog/post_detail.html', context=context)


def post_share(request, pk):
    post = get_object_or_404(Post, id=pk, status='published')
    sent = False
    cd = None
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']}({cd['email']})向你推荐了文章:{post.title}"
            message = f"{post.title}的地址:{post_url}\n\n{cd['name']}向您推荐的理由:{cd['comments']}"
            send_mail(subject, message, 'bluejack86@163.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post_share.html', {'post': post, 'form': form, 'sent': sent, 'cd': cd})
