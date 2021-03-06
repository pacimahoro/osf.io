"""Views tests for the Dropbox addon."""
import httplib as http
import unittest

from dropbox.rest import ErrorResponse
from nose.tools import assert_equal
from tests.base import OsfTestCase
from urllib3.exceptions import MaxRetryError

import mock
import pytest
from addons.base.tests import views as views_testing
from addons.dropbox.tests.utils import (DropboxAddonTestCase, MockDropbox,
                                        mock_responses, patch_client)
from osf_tests.factories import AuthUserFactory

from framework.auth import Auth
from addons.dropbox.serializer import DropboxSerializer
from addons.dropbox.views import dropbox_root_folder

mock_client = MockDropbox()
pytestmark = pytest.mark.django_db


class TestAuthViews(DropboxAddonTestCase, views_testing.OAuthAddonAuthViewsTestCaseMixin, OsfTestCase):

    @mock.patch(
        'addons.dropbox.models.Provider.auth_url',
        mock.PropertyMock(return_value='http://api.foo.com')
    )
    def test_oauth_start(self):
        super(TestAuthViews, self).test_oauth_start()

    @mock.patch('addons.dropbox.models.UserSettings.revoke_remote_oauth_access', mock.PropertyMock())
    def test_delete_external_account(self):
        super(TestAuthViews, self).test_delete_external_account()


class TestConfigViews(DropboxAddonTestCase, views_testing.OAuthAddonConfigViewsTestCaseMixin, OsfTestCase):

    folder = {
        'path': '12234',
        'id': '12234'
    }
    Serializer = DropboxSerializer
    client = mock_client

    @mock.patch('addons.dropbox.models.DropboxClient', return_value=mock_client)
    def test_folder_list(self, *args):
        super(TestConfigViews, self).test_folder_list()

    @mock.patch.object(DropboxSerializer, 'credentials_are_valid', return_value=True)
    def test_import_auth(self, *args):
        super(TestConfigViews, self).test_import_auth()


class TestFilebrowserViews(DropboxAddonTestCase, OsfTestCase):

    def setUp(self):
        super(TestFilebrowserViews, self).setUp()
        self.user.add_addon('dropbox')
        self.node_settings.external_account = self.user_settings.external_accounts[0]
        self.node_settings.save()

    def test_dropbox_folder_list(self):
        with patch_client('addons.dropbox.models.DropboxClient'):
            url = self.project.api_url_for(
                'dropbox_folder_list',
                folder_id='/',
            )
            res = self.app.get(url, auth=self.user.auth)
            contents = [x for x in mock_client.metadata('', list=True)['contents'] if x['is_dir']]
            first = res.json[0]

            assert len(res.json) == len(contents)
            assert 'kind' in first
            assert first['path'] == contents[0]['path']

    def test_dropbox_folder_list_if_folder_is_none_and_folders_only(self):
        with patch_client('addons.dropbox.models.DropboxClient'):
            self.node_settings.folder = None
            self.node_settings.save()
            url = self.project.api_url_for('dropbox_folder_list')
            res = self.app.get(url, auth=self.user.auth)
            contents = mock_client.metadata('', list=True)['contents']
            expected = [each for each in contents if each['is_dir']]
            assert len(res.json) == len(expected)

    def test_dropbox_folder_list_folders_only(self):
        with patch_client('addons.dropbox.models.DropboxClient'):
            url = self.project.api_url_for('dropbox_folder_list')
            res = self.app.get(url, auth=self.user.auth)
            contents = mock_client.metadata('', list=True)['contents']
            expected = [each for each in contents if each['is_dir']]
            assert len(res.json) == len(expected)

    @mock.patch('addons.dropbox.models.DropboxClient.metadata')
    def test_dropbox_folder_list_include_root(self, mock_metadata):
        with patch_client('addons.dropbox.models.DropboxClient'):
            url = self.project.api_url_for('dropbox_folder_list')

            res = self.app.get(url, auth=self.user.auth)
            contents = mock_client.metadata('', list=True)['contents']
            assert len(res.json) == 1
            assert len(res.json) != len(contents)
            assert res.json[0]['path'] == '/'

    @unittest.skip('finish this')
    def test_dropbox_root_folder(self):
        assert 0, 'finish me'

    def test_dropbox_root_folder_if_folder_is_none(self):
        # Something is returned on normal circumstances
        with mock.patch.object(type(self.node_settings), 'has_auth', True):
            root = dropbox_root_folder(node_settings=self.node_settings, auth=self.user.auth)

        assert root is not None

        # Nothing is returned when there is no folder linked
        self.node_settings.folder = None
        self.node_settings.save()
        with mock.patch.object(type(self.node_settings), 'has_auth', True):
            root = dropbox_root_folder(node_settings=self.node_settings, auth=self.user.auth)

        assert root is None

    @mock.patch('addons.dropbox.models.DropboxClient.metadata')
    def test_dropbox_folder_list_deleted(self, mock_metadata):
        # Example metadata for a deleted folder
        mock_metadata.return_value = {
            u'bytes': 0,
            u'contents': [],
            u'hash': u'e3c62eb85bc50dfa1107b4ca8047812b',
            u'icon': u'folder_gray',
            u'is_deleted': True,
            u'is_dir': True,
            u'modified': u'Sat, 29 Mar 2014 20:11:49 +0000',
            u'path': u'/tests',
            u'rev': u'3fed844002c12fc',
            u'revision': 67033156,
            u'root': u'dropbox',
            u'size': u'0 bytes',
            u'thumb_exists': False
        }
        url = self.project.api_url_for('dropbox_folder_list', folder_id='/tests')
        with mock.patch.object(type(self.node_settings), 'has_auth', True):
            res = self.app.get(url, auth=self.user.auth, expect_errors=True)

        assert res.status_code == http.NOT_FOUND

    @mock.patch('addons.dropbox.models.DropboxClient.metadata')
    def test_dropbox_folder_list_returns_error_if_invalid_path(self, mock_metadata):
        mock_response = mock.Mock()
        mock_metadata.side_effect = ErrorResponse(mock_response, body='File not found')
        url = self.project.api_url_for('dropbox_folder_list', folder_id='/fake_path')
        with mock.patch.object(type(self.node_settings), 'has_auth', True):
            res = self.app.get(url, auth=self.user.auth, expect_errors=True)
        assert res.status_code == http.NOT_FOUND

    @mock.patch('addons.dropbox.models.DropboxClient.metadata')
    def test_dropbox_folder_list_handles_max_retry_error(self, mock_metadata):
        mock_response = mock.Mock()
        url = self.project.api_url_for('dropbox_folder_list', folder_id='/')
        mock_metadata.side_effect = MaxRetryError(mock_response, url)
        with mock.patch.object(type(self.node_settings), 'has_auth', True):
            res = self.app.get(url, auth=self.user.auth, expect_errors=True)
        assert res.status_code == http.REQUEST_TIMEOUT


class TestRestrictions(DropboxAddonTestCase, OsfTestCase):

    def setUp(self):
        super(DropboxAddonTestCase, self).setUp()

        # Nasty contributor who will try to access folders that he shouldn't have
        # access to
        self.contrib = AuthUserFactory()
        self.project.add_contributor(self.contrib, auth=Auth(self.user))
        self.project.save()

        # Set shared folder
        self.node_settings.folder = 'foo bar/bar'
        self.node_settings.save()

    @mock.patch('addons.dropbox.models.DropboxClient.metadata')
    def test_restricted_folder_list(self, mock_metadata):
        mock_metadata.return_value = mock_responses['metadata_list']

        # tries to access a parent folder
        url = self.project.api_url_for('dropbox_folder_list',
            path='foo bar')
        res = self.app.get(url, auth=self.contrib.auth, expect_errors=True)
        assert_equal(res.status_code, http.FORBIDDEN)

    def test_restricted_config_contrib_no_addon(self):
        url = self.project.api_url_for('dropbox_set_config')
        res = self.app.put_json(url, {'selected': {'path': 'foo'}},
            auth=self.contrib.auth, expect_errors=True)
        assert_equal(res.status_code, http.BAD_REQUEST)

    def test_restricted_config_contrib_not_owner(self):
        # Contributor has dropbox auth, but is not the node authorizer
        self.contrib.add_addon('dropbox')
        self.contrib.save()

        url = self.project.api_url_for('dropbox_set_config')
        res = self.app.put_json(url, {'selected': {'path': 'foo'}},
            auth=self.contrib.auth, expect_errors=True)
        assert_equal(res.status_code, http.FORBIDDEN)
