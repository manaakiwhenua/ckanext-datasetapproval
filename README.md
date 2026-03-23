[![CKAN](https://img.shields.io/badge/ckan-2.9-orange.svg?style=flat-square)](https://github.com/ckan/ckan/tree/2.9)

# ckanext-datasetapproval
An extension which enforces private visibility of a dataset until it has been reviewed and approved by an organisation admin.

## Installation
To install ckanext-datasetapproval:

Note: if you're using `ckanext_scheming` extension, add new field to the schema configuration YAML file.

```
- field_name          : publishing_status
     label            : Publishing Status
     form_snippet     : null
     display_snippet  : null
     validators       : ignore_missing
```

```
- field_name          : chosen_visibility
     label            : Visibility
     form_snippet     : visibility.html
     display_snippet  : null
     validators       : ignore_empty unicode_safe
     default          : true
```
<br>

1. Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

    git clone https://github.com//ckanext-datasetapproval.git
    cd ckanext-datasetapproval
    pip install -e .
	pip install -r requirements.txt

3. Add `dataset_approval` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).
4. Add `ckanext.approval.turn_on_email_notifications` to the config file, to turn on/off review mail (this is set to `true` by default)
     <br>*Note: if you are using a dockerised CKAN environment add this environment variable to your .env file*
     ```CKANEXT__APPROVAL__TURN_ON_EMAIL_NOTIFICATIONS=false```

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     sudo service apache2 reload


## Approval Flow for Dataset
1. On create/update of a dataset, all editors can save their datasets as **in progress** to work on datasets without submitting for review.
<img width="893" height="78" alt="image" src="https://github.com/user-attachments/assets/fa9fabbb-bc76-48c0-831b-19ed7c0fc076" />
<img width="1258" height="367" alt="image" src="https://github.com/user-attachments/assets/4d9d8c1e-5ea6-471f-91cc-6e54b3a684dd" />

2. Only editors within any given organisation can submit a dataset for review.
<img width="855" height="72" alt="image" src="https://github.com/user-attachments/assets/94164b08-a15e-4ffd-b7e8-5e546191cd06" />

<br> **Editors get this message:**
<img width="1256" height="478" alt="image" src="https://github.com/user-attachments/assets/5fcf918c-8753-465d-8fce-9707d1ab5891" />

<br>*Note: All organisation admins are able to create and update datasets without having to submit for review.*

3. When a dataset is submitted for review, an email is sent to all admins (reviewers) of the specified organisation.
<img width="893" height="356" alt="image" src="https://github.com/user-attachments/assets/bbb2749e-6f1d-4c7f-9774-c5c434af2ffc" />

4. Users are able to view both their own datasets pending review and any submitted datasets they need to review
<br>	**An editor can see datasets they have requested for review**
<img width="1233" height="369" alt="image" src="https://github.com/user-attachments/assets/fb86524a-3a80-4952-9fee-2315ba5cef2a" />

<br>	**An admin can see datasets that they need to review**
<img width="1243" height="379" alt="image" src="https://github.com/user-attachments/assets/b3f785cd-cd04-46ab-a5cf-466c437158d2" />

6. To review, an admin of the organisation can choose to **approve** or **reject** the dataset
<img width="1249" height="496" alt="image" src="https://github.com/user-attachments/assets/a040f7e0-8130-4231-9cd1-c95c0f7829fb" />

 a. on reject they can add a rejection reason
 <img width="824" height="365" alt="image" src="https://github.com/user-attachments/assets/d963be7e-9b17-450b-bf54-684e28a82d07" />

 b. user is emailed their review outcome
 <img width="1157" height="314" alt="image" src="https://github.com/user-attachments/assets/b9884761-dbd3-477d-bcb5-5169d7f6e0a6" />

7. All datasets are enforced **private** until the dataset is approved. During **in progress** or on rejection, the dataset will remain private
     a. this means **in progress** and **rejected** datasets are only visible to organisation members

8. At any point (during or after dataset review), an editor can go back into the dataset, make changes, and submit for review again

