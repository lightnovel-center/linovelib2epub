import pkg_resources

print(__name__)

my_data = pkg_resources.resource_string(__name__, "./styles/chapter.css")

print(my_data)