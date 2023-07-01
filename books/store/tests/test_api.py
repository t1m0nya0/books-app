import json

from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BooksSerializer
from users.models import MyUser
from users.utils import get_tokens_for_user


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = MyUser.objects.create(email='test_username@mail.ru', date_of_birth="2004-02-09")
        self.book_1 = Book.objects.create(name='Test book 1',
                                          price=25, author_name='Author 1',
                                          owner=self.user)
        self.book_2 = Book.objects.create(name='Test book 2',
                                          price=45, author_name='Author 2')
        self.book_3 = Book.objects.create(name='Test book 3 Author 1',
                                          price=45, author_name='Author 3')

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 45})

        serilizer_data = BooksSerializer([self.book_2, self.book_3],
                                         many=True).data
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertEquals(serilizer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 1'})

        serilizer_data = BooksSerializer([self.book_1, self.book_3],
                                         many=True).data
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertEquals(serilizer_data, response.data)

    def test_get_ordering(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'price'})

        serilizer_data = BooksSerializer([self.book_1, self.book_2, self.book_3],
                                         many=True).data
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertEquals(serilizer_data, response.data)

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)

        serilizer_data = BooksSerializer([self.book_1, self.book_2, self.book_3],
                                         many=True).data
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertEquals(serilizer_data, response.data)

    def test_retrieve(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        response = self.client.get(url)

        serilizer_data = BooksSerializer(self.book_1,
                                         many=False).data
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertEquals(serilizer_data, response.data)

    def test_destroy(self):
        self.assertEquals(3, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book_1.id,))
        access_token = get_tokens_for_user(self.user)['access']

        response = self.client.delete(url, headers={"authorization": f"Bearer {access_token}"})

        self.assertEquals(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEquals(2, Book.objects.all().count())

    def test_create(self):
        self.assertEquals(3, Book.objects.all().count())
        url = reverse('book-list')

        data = {
            "name": "PP1",
            "price": 55,
            "author_name": "tamirlan"
        }
        access_token = get_tokens_for_user(self.user)['access']
        json_data = json.dumps(data)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json',
                                    headers={"authorization": f"Bearer {access_token}"})

        self.assertEquals(status.HTTP_201_CREATED, response.status_code)
        self.assertEquals(4, Book.objects.all().count())
        self.assertEquals(self.user, Book.objects.last().owner)

    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))

        data = {
            "name": self.book_1.name,
            "price": 55,
            "author_name": self.book_1.author_name
        }
        access_token = get_tokens_for_user(self.user)['access']
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data,
                                   content_type='application/json',
                                   headers={"authorization": f"Bearer {access_token}"})
        self.book_1.refresh_from_db()
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertEquals(55, self.book_1.price)

    def test_update_not_owner(self):
        self.user2 = MyUser.objects.create(email='test_username2@mail.ru',
                                           date_of_birth="2004-02-09")
        url = reverse('book-detail', args=(self.book_1.id,))

        data = {
            "name": self.book_1.name,
            "price": 55,
            "author_name": self.book_1.author_name
        }
        access_token = get_tokens_for_user(self.user2)['access']
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data,
                                   content_type='application/json',
                                   headers={"authorization": f"Bearer {access_token}"})
        self.book_1.refresh_from_db()
        self.assertEquals({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                 code='permission_denied')}, response.data)
        self.assertEquals(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEquals(25, self.book_1.price)

    def test_update_not_owner_but_staff(self):
        self.user2 = MyUser.objects.create(email='test_username2@mail.ru',
                                           date_of_birth="2004-02-09",
                                           is_admin=True)
        url = reverse('book-detail', args=(self.book_1.id,))

        data = {
            "name": self.book_1.name,
            "price": 55,
            "author_name": self.book_1.author_name
        }
        access_token = get_tokens_for_user(self.user2)['access']
        json_data = json.dumps(data)
        response = self.client.put(url, data=json_data,
                                   content_type='application/json',
                                   headers={"authorization": f"Bearer {access_token}"})
        self.book_1.refresh_from_db()
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.assertEquals(55, self.book_1.price)


class BooksRelationApiTestCase(APITestCase):
    def setUp(self):
        self.user = MyUser.objects.create(email='test_username@mail.ru', date_of_birth="2004-02-09")
        self.user2 = MyUser.objects.create(email='test_username2@mail.ru', date_of_birth="2004-02-09")
        self.book_1 = Book.objects.create(name='Test book 1',
                                          price=25, author_name='Author 1',
                                          owner=self.user)
        self.book_2 = Book.objects.create(name='Test book 2',
                                          price=45, author_name='Author 2')

    def test_like(self):
        url = reverse('userbookrelation-detail')
        data = {
            'like': True
        }
        access_token = get_tokens_for_user(self.user)['access']
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data,
                                   content_type='application/json',
                                   headers={"authorization": f"Bearer {access_token}"})
        self.assertEquals(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertTrue(self.book_1.like)

