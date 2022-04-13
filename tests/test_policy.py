from random import sample
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


@pytest.fixture
def sample_binding(sample_policy):
    return sample_policy.bindings[0]


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
