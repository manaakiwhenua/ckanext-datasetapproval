import pytest
import ckan.tests.helpers as test_helpers
import ckan.tests.factories as factories
import ckan.logic as logic

import logging
logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("standard_plugins")
class TestPackageCreate:
    @pytest.fixture(autouse=True)
    def _setup(
        self,
        make_org_with_member,
        make_dataset,
        make_context_for_editor_save,
        make_context_for_admin_save,
        
    ):
        self.make_org_with_member = make_org_with_member
        self.make_dataset = make_dataset
        self.make_context_for_editor_save = make_context_for_editor_save
        self.make_context_for_admin_save = make_context_for_admin_save
    
    def test_editor_create_dataset(self):
        editor = factories.User()
        org = self.make_org_with_member(editor, "editor")
        context = self.make_context_for_editor_save(editor)

        dataset = self.make_dataset(
            org["id"], 
            context
        )

        assert dataset["owner_org"] == org["id"]
        assert dataset["publishing_status"] == "in_progress"
    
    def test_admin_create_dataset(self):
        admin = factories.User()
        org = self.make_org_with_member(admin, "admin")
        context = self.make_context_for_admin_save(admin)

        test_dataset = self.make_dataset(
            org["id"], 
            context
        )

        assert test_dataset["owner_org"] == org["id"]
        assert test_dataset["publishing_status"] == "approved"

    # test user who is admin in org and editor in other org can create datasets
    def test_editor_admin_create_dataset(self):
        user = factories.User()
        org_with_editor = self.make_org_with_member(user, "editor")
        org_with_admin = self.make_org_with_member(user, "admin")

        editor_context = self.make_context_for_editor_save(user)
        admin_context = self.make_context_for_admin_save(user)


        created_as_editor = self.make_dataset(
            org_with_editor["id"], 
            editor_context
        )
        created_as_admin = self.make_dataset(
            org_with_admin["id"], 
            admin_context
        )


        assert created_as_editor["owner_org"] == org_with_editor["id"]
        assert created_as_editor["publishing_status"] == "in_progress"

        assert created_as_admin["owner_org"] == org_with_admin["id"]
        assert created_as_admin["publishing_status"] == "approved"

    def test_sysadmin_create_dataset(self):
        sysadmin = factories.Sysadmin()
        org = factories.Organization()
        context = self.make_context_for_admin_save(sysadmin)

        dataset = self.make_dataset(
            org["id"], 
            context
        )

        assert dataset["publishing_status"] == "approved"


@pytest.mark.usefixtures("standard_plugins")
class TestPackageUpdate:
    @pytest.fixture(autouse=True)
    def _setup(
        self,
        make_org_with_member,
        make_dataset,
        make_context_for_editor_save,
        make_context_for_editor_submit,
        make_context_for_editor_bypass,
        make_context_for_admin_save,
        
    ):
        self.make_org_with_member = make_org_with_member
        self.make_dataset = make_dataset
        self.make_context_for_editor_save = make_context_for_editor_save
        self.make_context_for_editor_submit = make_context_for_editor_submit
        self.make_context_for_editor_bypass = make_context_for_editor_bypass
        self.make_context_for_admin_save = make_context_for_admin_save
    
    def test_editor_save_in_progress(self):
        editor = factories.User()
        org = self.make_org_with_member(editor, "editor")

        context = self.make_context_for_editor_save(editor)
        test_dataset = self.make_dataset(
            org["id"], 
            context,
        )
        updated_dataset = test_helpers.call_action(
            "package_update",
            context=context,
            **test_dataset
        )

        assert updated_dataset["private"] == True
        assert updated_dataset["publishing_status"] == "in_progress"
    
    def test_editor_save_in_review_private(self):
        editor = factories.User()
        org = self.make_org_with_member(editor, "editor")
        save_context = self.make_context_for_editor_save(editor)
        in_progress_dataset = self.make_dataset(
            org["id"],
            save_context,
        )
        submit_context = self.make_context_for_editor_submit(editor)

        in_progress_dataset["chosen_visibility"] = "true"
        in_review_dataset = test_helpers.call_action(
            "package_update",
            context=submit_context,
            **in_progress_dataset
        )

        assert in_review_dataset["private"] == True
        assert in_review_dataset["chosen_visibility"] == "true"
        assert in_review_dataset["publishing_status"] == "in_review"

    def test_editor_save_in_review_public(self):
        editor = factories.User()
        org = self.make_org_with_member(editor, "editor")
        save_context = self.make_context_for_editor_save(editor)
        in_progress_dataset = self.make_dataset(
            org["id"],
            save_context,
        )
        submit_context = self.make_context_for_editor_submit(editor)

        in_progress_dataset["chosen_visibility"] = "false"
        in_review_dataset = test_helpers.call_action(
            "package_update",
            context=submit_context,
            **in_progress_dataset
        )

        assert in_review_dataset["private"] == True
        assert in_review_dataset["chosen_visibility"] == "false"
        assert in_review_dataset["publishing_status"] == "in_review"

    def test_editor_saves_approved_as_in_progress(self):
        sysadmin = factories.Sysadmin()
        editor = factories.User()
        org = self.make_org_with_member(editor, "editor")
        admin_context = self.make_context_for_admin_save(sysadmin)
        approved_dataset = self.make_dataset(
            org["id"],
            admin_context,
        )
        save_context = self.make_context_for_editor_save(editor)
        chosen_visibility = approved_dataset["chosen_visibility"]


        saved_dataset = test_helpers.call_action(
            "package_update",
            context=save_context,
            **approved_dataset
        )

        assert saved_dataset["private"] == True
        assert saved_dataset["chosen_visibility"] == chosen_visibility
        assert saved_dataset["publishing_status"] == "in_progress"

    def test_editor_saves_approved_as_in_review(self):
        sysadmin = factories.Sysadmin()
        editor = factories.User()
        org = self.make_org_with_member(editor, "editor")
        admin_context = self.make_context_for_admin_save(sysadmin)
        approved_dataset = self.make_dataset(
            org["id"],
            admin_context,
        )
        save_context = self.make_context_for_editor_submit(editor)
        chosen_visibility = approved_dataset["chosen_visibility"]

        saved_dataset = test_helpers.call_action(
            "package_update",
            context=save_context,
            **approved_dataset
        )

        assert saved_dataset["private"] == True
        assert saved_dataset["chosen_visibility"] == chosen_visibility
        assert saved_dataset["publishing_status"] == "in_review"

    def test_editor_bypasses_review(self):
        sysadmin = factories.Sysadmin()
        editor = factories.User()
        org = self.make_org_with_member(editor, "editor")
        admin_context = self.make_context_for_admin_save(sysadmin)
        approved_dataset = self.make_dataset(
            org["id"],
            admin_context,
        )
        save_context = self.make_context_for_editor_bypass(editor)
        patch = {
            "id": approved_dataset["id"],
            "chosen_visibility": approved_dataset["chosen_visibility"],
            "private": approved_dataset["private"],
        }

        updated_dataset = test_helpers.call_action(
            "package_patch",
            context=save_context,
            **patch
        )

        assert updated_dataset["private"] == (
            updated_dataset["chosen_visibility"] == "true"
        )
        assert updated_dataset["publishing_status"] == "approved"

    def test_editor_bypasses_review_invalid_dataset(self):
        sysadmin = factories.Sysadmin()
        editor = factories.User()
        org = self.make_org_with_member(editor, "editor")
        admin_context = self.make_context_for_admin_save(sysadmin)
        invalid_dataset = self.make_dataset(
            org["id"],
            admin_context,
        )
        invalid_dataset["notes"] = ""
        patch = {
            "id": invalid_dataset["id"],
            "chosen_visibility": "true",
            "private": invalid_dataset["private"],
            "notes": "",
        }
        save_context = self.make_context_for_editor_bypass(editor)

        with pytest.raises(logic.ValidationError):
            updated_dataset = test_helpers.call_action(
                "package_patch",
                context=save_context,
                **patch
            )

            assert updated_dataset["chosen_visibility"] != "true"
            assert updated_dataset["publishing_status"] != "approved"

    def test_editor_saves_in_review_invalid_dataset(self):
        sysadmin = factories.Sysadmin()
        editor = factories.User()
        org = self.make_org_with_member(editor, "editor")
        admin_context = self.make_context_for_admin_save(sysadmin)
        invalid_dataset = self.make_dataset(
            org["id"],
            admin_context,
        )
        invalid_dataset["notes"] = ""
        invalid_dataset["chosen_visibility"] == "true"
        save_context = self.make_context_for_editor_submit(editor)

        with pytest.raises(logic.ValidationError):
            updated_dataset = test_helpers.call_action(
                "package_update",
                context=save_context,
                **invalid_dataset
            )
            
            assert updated_dataset["chosen_visibility"] != "true"
            assert updated_dataset["publishing_status"] != "in_review"

    def test_admin_saves_approved_as_public(self):
        admin = factories.User()
        org = self.make_org_with_member(admin, "admin")
        admin_context = self.make_context_for_admin_save(admin)
        approved_dataset = self.make_dataset(
            org["id"],
            admin_context,
        )
        approved_dataset["private"] = False
        
        updated_dataset = test_helpers.call_action(
            "package_update",
            context=admin_context,
            **approved_dataset
        )

        assert updated_dataset["private"] == False
        assert updated_dataset["private"] == (
            updated_dataset["chosen_visibility"] == "true"
        )
        assert updated_dataset["publishing_status"] == "approved"
    
    def test_admin_saves_approved_as_private(self):
        admin = factories.User()
        org = self.make_org_with_member(admin, "admin")
        admin_context = self.make_context_for_admin_save(admin)
        approved_dataset = self.make_dataset(
            org["id"],
            admin_context,
        )
        approved_dataset["private"] = True
        
        updated_dataset = test_helpers.call_action(
            "package_update",
            context=admin_context,
            **approved_dataset
        )

        assert updated_dataset["private"] == True
        assert updated_dataset["private"] == (
            updated_dataset["chosen_visibility"] == "true"
        )
        assert updated_dataset["publishing_status"] == "approved"