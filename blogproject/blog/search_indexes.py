from haystack import indexes
from .models import Post


class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):#索引服务于那个模型
        return Post

    def index_queryset(self, using=None):
        return self.get_model().objects.all()