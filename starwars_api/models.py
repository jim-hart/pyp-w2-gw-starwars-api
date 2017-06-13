from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError
import six

api_client = SWAPIClient()

class BaseModel(object):

    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        """
        for k, v in six.iteritems(json_data):
            setattr(self, k, v)

    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        return cls(getattr(api_client, 'get_'+cls.RESOURCE_NAME)(resource_id))


    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        query = cls.RESOURCE_NAME.title() + 'QuerySet'
        return globals()[query]()


class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        return 'Person: {0}'.format(self.name)


class Films(BaseModel):
    RESOURCE_NAME = 'films'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object):

    def __init__(self):
        self.objects = []
        self.page = 0
        self.obj_count = 0

    def __iter__(self):
        return self.__class__()

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        while True:
            if self.obj_count >= len(self.objects):
                try:
                    self._get_next_page()
                except SWAPIClientError:
                    raise StopIteration

            self.obj_count += 1
            return self.objects[self.obj_count-1]
    
    next = __next__

    def _get_next_page(self):

        self.page += 1
        data = getattr(api_client, 'get_'+self.RESOURCE_NAME)(page=self.page)

        while data['results']:
            new_obj = globals()[self.RESOURCE_NAME.title()](data['results'].pop(0))
            self.objects.append(new_obj)

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        return getattr(api_client, 'get_'+self.RESOURCE_NAME)()['count']



class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self):
        super(PeopleQuerySet, self).__init__()

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self):
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))
