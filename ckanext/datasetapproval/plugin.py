import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.plugins import DefaultPermissionLabels
from ckanext.datasetapproval import actions, blueprints, helpers, views, workflow_action_helpers, auth
import logging as log
from ckan.common import _, c

log = log.getLogger(__name__)

class DatasetapprovalPlugin(plugins.SingletonPlugin, 
        DefaultPermissionLabels, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IPermissionLabels, inherit=True)
    plugins.implements(plugins.IAuthFunctions)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('assets',
            'datasetapproval')

   # IActions
    def get_actions(self):
        return {
            'package_create': actions.package_create,
            'package_show': actions.package_show,
            'package_update': actions.package_update,
            'resource_create': actions.resource_create,
            'resource_update': actions.resource_update,
            'check_user_admin': actions.check_user_admin,
            'retrieve_rejection_reasons': actions.retrieve_rejection_reasons,
            'workflow_actions_show': actions.workflow_actions_show,
            'latest_workflow_action_show': actions.latest_workflow_action_show,
            'retrieve_publishing_status': actions.retrieve_publishing_status
        }

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        return True

    def package_types(self):
        # registers itself as the default (above).
        return []

    # ITemplateHelpers
    def get_helpers(self):
        helper_functions = {}

        helper_functions.update(helpers.get_helpers())
        helper_functions.update(workflow_action_helpers.get_helpers())
        return helper_functions

    # IBlueprint
    def get_blueprint(self):
        full_blueprints = [views.dataset.registered_views(),  blueprints.approveBlueprint]
        return full_blueprints

    # IPackageController
    def before_dataset_view(self, pkg_dict):
        '''
        This method is called before rendering the read.html page.
        You can add extra variables to the pkg_dict here which can then be accessed in the read.html template.
        '''
        try:
            endpoint = toolkit.request.endpoint
        except RuntimeError:
            return pkg_dict

        # Add latest workflow action details and additional reviews requested to the dataset read page. No permissions or workflow action comments are required.
        if endpoint and endpoint.endswith('dataset.read'):
            latest_workflow_action = toolkit.get_action('latest_workflow_action_show')(
                {},
                {'id': pkg_dict['id']}
            )
            pkg_dict['latest_workflow_action'] = latest_workflow_action
            pkg_dict['additional_reviews_requested'] = helpers.get_review_types_for_display(pkg_dict)
        return pkg_dict
        
    # IAuthFunctions
    def get_auth_functions(self):
        return auth.get_auth_functions()
