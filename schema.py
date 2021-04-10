import graphene
import json
import uuid
from datetime import datetime


class Post(graphene.ObjectType):
    title = graphene.String()
    content = graphene.String()


class User(graphene.ObjectType):
    id = graphene.ID(default_value=str(uuid.uuid4()))
    username = graphene.String()
    created_at = graphene.DateTime(default_value=datetime.now())
    avatar_url = graphene.String()

    def resolve_avatar_url(self, info):
        return 'https://cloudinary.com/{}/{}'.format(self.username, self.id)


class Query(graphene.ObjectType):
    hello = graphene.String()
    is_admin = graphene.Boolean()
    users = graphene.List(User, limit=graphene.Int())

    def resolve_hello(self, info):
        return "world"

    def resolve_is_admin(self, info):
        return True

    def resolve_users(self, info, limit=None):
        # default values make the arguement optional
        return [
            User(id="1", username="Fred", created_at=datetime.now()),
            User(id="2", username="Mary", created_at=datetime.now()),
            User(id="3", username="Jim", created_at=datetime.now()),
        ][:limit]


class CreateUser(graphene.Mutation):
    user = graphene.Field(User)

    class Arguments:
        username = graphene.String()

    def mutate(self, info, username):
        user = User(username=username)
        return CreateUser(user=user)


class CreatePost(graphene.Mutation):
    post = graphene.Field(Post)

    class Arguments:
        title = graphene.String()
        content = graphene.String()

    def mutate(self, info, title, content):
        is_anonymous = info.context.get('is_anonymous')
        if is_anonymous:
            raise Exception('Not Authenticated')
        post = Post(title=title, content=content)
        return CreatePost(post=post)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_post = CreatePost.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

result = schema.execute(
    '''
    query getUsersQuery ($limit: Int) {
        hello
        isAdmin
        users(limit: $limit) {
            id
            username
            createdAt
            avatarUrl
        }
    }
    ''',
    variable_values={'limit': 1}
)

dictResult = dict(result.data.items())

print(json.dumps(dictResult, indent=2))

result = schema.execute(
    '''
    mutation($username: String) {
       createUser(username: $username) {
           user {
               id
               username
           }
       }
    } 
    ''',
    variable_values={'username': 'Freddo Bar'}
)

result = schema.execute(
    '''
    mutation {
        createPost(title: "Hello", content: "World") {
            post {
                title
                content
            }
        }
    }
    ''',
    context={
        'is_anonymous': False
    }
)

# print(result)

dictResult = dict(result.data.items())

print(json.dumps(dictResult, indent=2))
