from .models import Category

def global_context(request):
    roots = Category.objects.root_nodes().all()
    navs = []
    for root in roots:
        item = {}
        item['name'] = root.name
        item['id'] = root.id
        item['subs'] = root.children.values('name', 'id')
        item['arts'] = root.article_set.values('name', 'id')
        navs.append(item)
    return {'blog_navbar': navs, 'domain': 'jiangengdong.top'}
