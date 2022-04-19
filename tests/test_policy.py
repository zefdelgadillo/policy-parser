from pparse.policy import Policy
import pytest
import yaml
import os


@pytest.fixture
def sample_policy():
    f = open(
        os.path.join(os.path.dirname(__file__),
                     'fixtures/policy-fixture.yaml'), "r")
    policy_dict = yaml.safe_load(f.read())
    return Policy().from_dict(policy_dict)


@pytest.fixture
def sample_binding(sample_policy):
    return sample_policy.bindings[0]


def test_policy_contains_bindings_list(sample_policy):
    assert isinstance(sample_policy.bindings, list)
    assert isinstance(sample_policy.bindings[0], type(Policy().Binding()))


def test_policy_contains_version(sample_policy):
    assert isinstance(sample_policy.version, int)
    assert sample_policy.version != ''


def test_policy_contains_etag(sample_policy):
    assert isinstance(sample_policy.etag, str)
    assert sample_policy.etag != ''


def test_policy_returns_dict(sample_policy):
    assert isinstance(sample_policy.to_dict(), dict)


def test_policy_returns_principals(sample_policy):
    principals = sample_policy.principals()
    assert len(principals) == 23
    assert not list(principals)[0].startswith('serviceAccount')
    assert not list(principals)[0].startswith('user')
    assert not list(principals)[0].startswith('group')
    assert not list(principals)[0].startswith('domain')


def test_policy_returns_members(sample_policy):
    members = sample_policy.members()
    assert len(members) == 23
    assert list(members)[0].startswith('user') or list(members)[0].startswith(
        'group') or list(members)[0].startswith('serviceAccount') or list(
            members)[0].startswith('domain')


def test_policy_filter_by_principals(sample_policy):
    test_principals = ['annbaker@company.com', 'louiefranco@company.com']
    sample_policy.filter_bindings_by_principals(test_principals)
    assert sample_policy.principals() == set(test_principals)


def test_policy_filter_by_empty_principal(sample_policy):
    fixture_policy = sample_policy
    sample_policy.filter_bindings_by_principals([])
    assert fixture_policy == sample_policy


def test_policy_filter_by_roles(sample_policy):
    test_roles = ['roles/owner', 'roles/editor']
    sample_policy.filter_bindings_by_roles(test_roles)
    assert sample_policy.roles() == set(test_roles)


def test_policy_filter_by_invalid_roles(sample_policy):
    test_roles = ['roles/owner', 'roles/editor']
    sample_policy.filter_bindings_by_roles(test_roles)
    assert sample_policy.roles() == set(test_roles)


def test_policy_filter_by_empty_role(sample_policy):
    fixture_policy = sample_policy
    sample_policy.filter_bindings_by_roles([])
    assert fixture_policy == sample_policy


def test_policy_filter_by_type(sample_policy):
    test_users = {
        'annbaker@company.com', 'jimmyjohn@company.com',
        'louiefranco@company.com', 'rhondaseltzer@company.com'
    }
    sample_policy.filter_bindings_by_type('user')
    assert sample_policy.principals() == set(test_users)


def test_policy_filter_by_empty_type(sample_policy):
    fixture_policy = sample_policy
    sample_policy.filter_bindings_by_type('')
    assert fixture_policy == sample_policy


def test_binding_contains_role(sample_binding):
    assert isinstance(sample_binding.role, str)
    assert sample_binding.role == 'roles/cloudbuild.builds.builder'


def test_binding_contains_members(sample_binding):
    assert isinstance(sample_binding.members, list)


def test_binding_member_member(sample_binding):
    assert sample_binding.members[
        0].member == 'serviceAccount:555555555555@cloudbuild.gserviceaccount.com'


def test_binding_member_principal_type(sample_binding):
    assert sample_binding.members[0].principal_type == 'serviceAccount'


def test_binding_member_principal(sample_binding):
    assert sample_binding.members[
        0].principal == '555555555555@cloudbuild.gserviceaccount.com'
