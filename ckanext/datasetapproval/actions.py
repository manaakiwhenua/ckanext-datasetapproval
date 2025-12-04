import logging
import ckan.authz as authz

from ckan.lib.mailer import MailerException
import ckan.plugins.toolkit as tk
import ckan.plugins as p
import ckan.logic as logic

from ckanext.datasetapproval.mailer import mail_package_review_request_to_admins, mail_package_approve_reject_notification_to_editors

log = logging.getLogger(__name__)

def is_user_editor_of_org(org_id, user_id):
    capacity = authz.users_role_for_group_or_org(org_id, user_id)
    return capacity == "editor"

def publishing_check(context, data_dict):
    admin_editing = context.get("admin_editing", False)
    submit_review = context.get("submit_review", False)
    log.debug("publishing_check context: %r", context)
    user_id = (
        tk.current_user.id
        if tk.current_user and not tk.current_user.is_anonymous
        else None
    )
    org_id = data_dict.get("owner_org")

    if data_dict.get("currently_reviewing"):
        data_dict.pop("currently_reviewing")
        if data_dict.get("publishing_status") == "approved":
            data_dict["private"] = data_dict.get("chosen_visibility", "true") == "true"
        elif data_dict.get("publishing_status") == "rejected":
            data_dict["private"] = "true"
        #mail_package_approve_reject_notification_to_editors(data_dict.get("id"), data_dict.get("publishing_status"))
    elif admin_editing and data_dict.get("id"):
        old_data_dict = tk.get_action("package_show")(
            context, {"id": data_dict.get("id")}
        )
        if old_data_dict.get("publishing_status") == "in_review":
            data_dict["publishing_status"] = old_data_dict.get("publishing_status")
        data_dict["chosen_visibility"] = data_dict.get("private", "true")
    elif is_user_editor_of_org(org_id, user_id):
        if submit_review:
            #mail_package_review_request_to_admins(context, data_dict)
            data_dict['publishing_status'] = "in_review"
        else:
            data_dict["private"] = "true"
            data_dict['publishing_status'] = "in_progress"
    log.debug("publishing_check final data_dict: %r", data_dict)
    return data_dict


@tk.chained_action
@logic.side_effect_free
def package_show(up_func, context, data_dict):
    tk.check_access('package_show_with_approval', context, data_dict)
    return up_func(context, data_dict)

@tk.chained_action
@logic.side_effect_free
def package_create(up_func, context, data_dict):
    publishing_check(context, data_dict)
    result = up_func(context, data_dict)
    return result


@tk.chained_action
@logic.side_effect_free
def package_update(up_func, context, data_dict):
    publishing_check(context, data_dict)
    result = up_func(context, data_dict)
    return result


@tk.chained_action
@logic.side_effect_free
def package_patch(up_func, context, data_dict):
    publishing_check(context, data_dict)
    result = up_func(context, data_dict)
    return result

@p.toolkit.chained_action   
def resource_create(up_func,context, data_dict):
    publishing_check(context, data_dict)
    result = up_func(context, data_dict)
    return result

@p.toolkit.chained_action   
def resource_update(up_func,context, data_dict):
    publishing_check(context, data_dict)
    result = up_func(context, data_dict)
    return result