# LMS Integration

## Canvas

The setup for the Canvas LMS.

### Configure the JupyterHub as a Developer Key

1. [To install the JupyterHub as an External Tool](https://community.canvaslms.com/t5/Canvas-Releases-Board/Canvas-Release-LTI-1-3-and-LTI-Advantage-2019-06-22/td-p/246652) admin users need to create a `Developer Key`.
   (More detailed instructions and screenshots on how to access this section are provided in the link above).

2. Once the Developer Key configuration is open, select the `Enter URL` method within the `Configure` → `Method` dropdown.
   This allows admin users to add the JupyterHub configuration by referring to a JupyterHub endpoint that renders the LTI 1.3 configuration in JSON.
   By default, the configuration URL is structured with the `https://<my-hub.domain.com>/hub/lti13/config` format.

3. Add the `Redirect URIs`.
   By default, the redirect URI is equivalent to the callback URL.
   As such the default URL for the Redirect URIs field should be `https://<my-hub.domain.com>/hub/lti13/oauth_callback`.

4. Add a `Key Name` to identify the `Developer Key`.

5. (Optional) Enter owner's email and `Developer Key` notes.

6. Save the `Developer Key` settings by clicking on the `Save` button.

### Enable the Developer Key and copy Client ID

1. You should now see the new `Developer Key` in the `Admin` → `Developer Keys` → `Accounts` tab.
   By default, the `Developer Key` is disabled.
   Enable the JupyterHub installation by clicking on the On/Off toggle in the `State` column to switch it to `ON`.

2. Copy the value that represents the `Client ID` in the `Datails` column.
   This value should look something like `125900000000000318`.
   You will need to enter this value in the [JupyterHub config](getting-started.md#basic-settings).

### Install the JupyterHub as an External Tool in your Canvas Course

1. Navigate to the course where you would like to enable the JupyterHub.

1. Click on the course's `Settings` link.

1. Click on the `Apps` tab and then on `View App Configurations`.

1. Click on the `+App` button to add a new application.
   Select `By Client ID` from the `Configuration Type` dropdown and paste the `Client ID` value that you copied from the `Developer Keys` → `<Your Developer Key Name>` → `Details` column.

1. Save the application.

Once the application is saved you will see the option to launch the JupyterHub from the Course navigation menu. You will also have the option to add `Assignments` as an `External Tool`.

**Privacy Settings**:

The LTI 1.3 External Tool application in [Canvas may be configured with privacy enabled](https://community.canvaslms.com/t5/Canvas-Developers-Group/LTI-1-3-Configuration-Claims-Course-Placement-Privacy/td-p/229252). The user ID in these cases will fetch the value from the LTI 1.3 subject (`sub` claim) which is a unique and opaque identifier for the student.

### Create a new assignment as an External Tool

1. Navigate to `Assignments` → `Add Assignment`
2. For `Submission Type`, select `External Tool`
3. **IMPORTANT:** Click on the `Find` button and search for the external tool by the name that you added in the step above.
   Selecting the external tool will prepopulate the URL field with the correct launch URL.
   Using the `Find` button to search for your external tool is necessary to ensure that the `client_id` is referenced correctly.
4. (Recommended) Check the `Launch in a new tab` checkbox.
5. Append any custom parameters you wish (see next step)

```{note}
If you are creating assignments via the Canvas API, you need to use [these undocumented external tool fields](https://github.com/instructure/canvas-lms/issues/1315) when creating the assignment.
```

6. **Custom Parameters**: With Canvas users have the option to set [custom fields](https://community.canvaslms.com/t5/Admin-Guide/How-do-I-configure-a-manual-entry-external-app-for-an-account/ta-p/219#add_custom_fields_and_descriptions) with the Launch Request URL.
   Also, [LTI variable substitution](https://canvas.instructure.com/doc/api/file.tools_variable_substitutions.html) is available.
