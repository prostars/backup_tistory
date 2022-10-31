# https://tistory.github.io/document-tistory-apis
BASE_URL = 'https://www.tistory.com'
BLOG_POST_LIST = BASE_URL + '/apis/post/list'
BLOG_POST_READ = BASE_URL + '/apis/post/read'

# 글 목록 API
# https://tistory.github.io/document-tistory-apis/apis/v1/post/list.html
class ParamsForPostList:
    def __init__(self, access_token, blog_name, page, output='json'):
        self.access_token = access_token
        self.blog_name = blog_name
        self.page = page
        self.output = output

    def get_params(self):
        return {
            'access_token': self.access_token,
            'blogName': self.blog_name,
            'page': self.page,
            'output': self.output
        }


# 글 읽기 API
# https://tistory.github.io/document-tistory-apis/apis/v1/post/read.html
class ParamsForPostRead:
    def __init__(self, access_token, blog_name, post_id, output='json'):
        self.access_token = access_token
        self.blog_name = blog_name
        self.post_id = post_id
        self.output = output

    def get_params(self):
        return {
            'access_token': self.access_token,
            'blogName': self.blog_name,
            'postId': self.post_id,
            'output': self.output
        }
