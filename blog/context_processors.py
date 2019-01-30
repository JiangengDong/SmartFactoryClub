from .models import Category

def global_context(request):
    roots = Category.objects.root_nodes().all()
    navs = []
    for root in roots:
        item = {}
        item['name'] = root.name
        item['subs'] = root.children.values('name')
        item['arts'] = root.article_set.values('name')
        navs.append(item)
    return {'blog_navbar': navs}
