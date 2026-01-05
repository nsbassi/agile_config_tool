Ext.define("AgileAcpt.view.config.ConfigPanel", {
  extend: "Ext.panel.Panel",
  xtype: "config-panel",
  requires: ["AgileAcpt.controller.Config"],
  controller: "config",
  layout: {
    type: "vbox",
    align: "stretch",
  },
  scrollable: true,
  items: [
    {
      xtype: "panel",
      title: "Environments",
      collapsible: true,
      flex: 1,
      minHeight: 400,
      scrollable: true,
      layout: {
        type: "hbox",
        align: "stretch",
      },
      items: [
        {
          xtype: "grid",
          reference: "envGrid",
          flex: 1,
          store: {
            fields: [
              "id",
              "tag",
              "agilePlmUrl",
              "propagationUser",
              "propagationPassword",
              "destJdbcUrl",
              "destTnsName",
              "destOracleHome",
              "destDbUser",
              "destDbPassword",
              "acpProjectDir",
            ],
            proxy: {
              type: "rest",
              url: "/api/environments",
              reader: {
                type: "json",
                rootProperty: "data",
              },
              writer: {
                type: "json",
                writeAllFields: true,
              },
              headers: {
                Authorization: "Bearer " + localStorage.getItem("jwt"),
              },
            },
            autoLoad: true,
          },
          columns: [
            {
              text: "Environment Tag",
              dataIndex: "tag",
              flex: 1,
            },
            {
              text: "Agile PLM URL",
              dataIndex: "agilePlmUrl",
              flex: 2,
            },
            {
              text: "Propagation User",
              dataIndex: "propagationUser",
              flex: 1,
            },
            {
              xtype: "actioncolumn",
              width: 80,
              text: "Actions",
              items: [
                {
                  iconCls: "fas fa-edit",
                  tooltip: "Edit",
                  handler: "onEditEnvironment",
                },
                {
                  iconCls: "fas fa-trash",
                  tooltip: "Delete",
                  handler: "onDeleteEnvironment",
                },
              ],
            },
          ],
          tbar: [
            {
              text: "Add Environment",
              iconCls: "fas fa-plus",
              handler: "onAddEnvironment",
            },
          ],
        },
        {
          xtype: "form",
          reference: "envForm",
          title: "Environment Details",
          hidden: true,
          width: 450,
          bodyPadding: 20,
          scrollable: true,
          defaults: {
            xtype: "textfield",
            anchor: "100%",
            labelWidth: 150,
            margin: "10 0",
          },
          items: [
            {
              xtype: "hiddenfield",
              name: "id",
            },
            {
              fieldLabel: "Environment Tag",
              name: "tag",
              allowBlank: false,
              emptyText: "e.g., Dev, QA, Prod",
            },
            {
              xtype: "fieldset",
              title: "PLM Instance Details (For ACP)",
              collapsible: true,
              collapsed: false,
              defaults: {
                xtype: "textfield",
                anchor: "100%",
                labelWidth: 150,
                margin: "5 0",
              },
              items: [
                {
                  fieldLabel: "Agile PLM URL",
                  name: "agilePlmUrl",
                  allowBlank: false,
                  emptyText: "http://agile-server:port",
                },
                {
                  fieldLabel: "Propagation User",
                  name: "propagationUser",
                  allowBlank: false,
                },
                {
                  fieldLabel: "Propagation Password",
                  name: "propagationPassword",
                  inputType: "password",
                  allowBlank: false,
                  triggers: {
                    eye: {
                      cls: "fas fa-eye",
                      handler: function (field) {
                        var trigger = field.getTrigger("eye");
                        if (field.inputType === "password") {
                          field.inputType = "text";
                          field.inputEl.dom.type = "text";
                          trigger.el.replaceCls("fa-eye", "fa-eye-slash");
                        } else {
                          field.inputType = "password";
                          field.inputEl.dom.type = "password";
                          trigger.el.replaceCls("fa-eye-slash", "fa-eye");
                        }
                      },
                    },
                  },
                },
                {
                  fieldLabel: "ACP Project Directory",
                  name: "acpProjectDir",
                  emptyText: "/path/to/acp/scripts",
                  tooltip:
                    "Server directory where ACP scripts are located. Config file will be copied here as config.xml",
                },
              ],
            },
            {
              xtype: "fieldset",
              title: "Destination Database Details (For Averify)",
              collapsible: true,
              collapsed: true,
              defaults: {
                xtype: "textfield",
                anchor: "100%",
                labelWidth: 150,
                margin: "5 0",
              },
              items: [
                {
                  fieldLabel: "Dest JDBC URL",
                  name: "destJdbcUrl",
                  emptyText: "jdbc:oracle:thin:@dest_host:port:sid",
                },
                {
                  fieldLabel: "Dest TNS Name",
                  name: "destTnsName",
                  emptyText: "TNS entry name",
                },
                {
                  fieldLabel: "Dest Oracle Home",
                  name: "destOracleHome",
                  emptyText: "d:/oracle/ora92",
                },
                {
                  fieldLabel: "Dest DB User",
                  name: "destDbUser",
                  emptyText: "Database username",
                },
                {
                  fieldLabel: "Dest DB Password",
                  name: "destDbPassword",
                  inputType: "password",
                  emptyText: "Database password",
                  triggers: {
                    eye: {
                      cls: "fas fa-eye",
                      handler: function (field) {
                        var trigger = field.getTrigger("eye");
                        if (field.inputType === "password") {
                          field.inputType = "text";
                          field.inputEl.dom.type = "text";
                          trigger.el.replaceCls("fa-eye", "fa-eye-slash");
                        } else {
                          field.inputType = "password";
                          field.inputEl.dom.type = "password";
                          trigger.el.replaceCls("fa-eye-slash", "fa-eye");
                        }
                      },
                    },
                  },
                },
              ],
            },
          ],
          buttons: [
            {
              text: "Save",
              iconCls: "fas fa-save",
              formBind: true,
              handler: "onSaveEnvironment",
            },
            {
              text: "Cancel",
              handler: "onCancelEdit",
            },
          ],
        },
      ],
    },
    {
      xtype: "form",
      reference: "hostConfigForm",
      title: "ACP/Averify Host Details",
      collapsible: true,
      collapsed: false,
      bodyPadding: 20,
      scrollable: true,
      layout: {
        type: "vbox",
        align: "center",
      },
      defaults: {
        width: 600,
        labelWidth: 150,
        margin: "10 0",
      },
      items: [
        {
          xtype: "combo",
          fieldLabel: "Execution Mode",
          name: "executionMode",
          reference: "executionMode",
          allowBlank: false,
          editable: false,
          value: "local",
          displayField: "name",
          valueField: "value",
          store: {
            fields: ["name", "value"],
            data: [
              { name: "Local", value: "local" },
              { name: "Remote", value: "remote" },
            ],
          },
          listeners: {
            change: "onExecutionModeChange",
          },
        },
        {
          xtype: "textfield",
          fieldLabel: "ACP Base Directory",
          name: "acpBaseDir",
          allowBlank: false,
          emptyText: "/path/to/acp/base/directory",
        },
        {
          xtype: "textfield",
          fieldLabel: "Averify Base Directory",
          name: "averifyBaseDir",
          allowBlank: false,
          emptyText: "/path/to/averify/base/directory",
        },
        {
          xtype: "fieldset",
          title: "Remote Execution Settings",
          reference: "remoteFieldset",
          hidden: true,
          collapsible: false,
          width: 600,
          defaults: {
            xtype: "textfield",
            anchor: "100%",
            labelWidth: 150,
            margin: "5 0",
          },
          items: [
            {
              fieldLabel: "Host",
              name: "remoteHost",
              emptyText: "Remote server hostname or IP",
            },
            {
              fieldLabel: "OS User",
              name: "remoteUser",
              emptyText: "Username for remote connection",
            },
            {
              xtype: "radiogroup",
              fieldLabel: "Authentication",
              name: "authType",
              reference: "authType",
              columns: 2,
              vertical: false,
              items: [
                { boxLabel: "Password", name: "authType", inputValue: "password", checked: true },
                { boxLabel: "SSH Key", name: "authType", inputValue: "sshkey" },
              ],
              listeners: {
                change: "onAuthTypeChange",
              },
            },
            {
              fieldLabel: "Password",
              name: "remotePassword",
              reference: "remotePassword",
              inputType: "password",
              emptyText: "Remote user password",
              triggers: {
                eye: {
                  cls: "fas fa-eye",
                  handler: function (field) {
                    var trigger = field.getTrigger("eye");
                    if (field.inputType === "password") {
                      field.inputType = "text";
                      field.inputEl.dom.type = "text";
                      trigger.el.replaceCls("fa-eye", "fa-eye-slash");
                    } else {
                      field.inputType = "password";
                      field.inputEl.dom.type = "password";
                      trigger.el.replaceCls("fa-eye-slash", "fa-eye");
                    }
                  },
                },
              },
            },
            {
              xtype: "filefield",
              fieldLabel: "SSH Key File",
              name: "sshKeyPath",
              reference: "sshKeyPath",
              hidden: true,
              buttonText: "Browse...",
              emptyText: "Select SSH private key file",
            },
            {
              fieldLabel: "SSH Port",
              name: "sshPort",
              value: "22",
              emptyText: "22",
            },
          ],
        },
        {
          xtype: "fieldset",
          title: "Email Configuration (For Averify)",
          reference: "emailFieldset",
          collapsible: false,
          width: 600,
          defaults: {
            xtype: "textfield",
            anchor: "100%",
            labelWidth: 150,
            margin: "5 0",
          },
          items: [
            {
              fieldLabel: "Customer Name",
              name: "customerName",
              emptyText: "Customer name for Averify reports",
            },
            {
              fieldLabel: "Mail Host",
              name: "mailHost",
              emptyText: "SMTP server hostname",
            },
            {
              fieldLabel: "Mail Port",
              name: "mailPort",
              value: "25",
              emptyText: "SMTP port (default: 25)",
            },
            {
              fieldLabel: "From Address",
              name: "fromAddress",
              vtype: "email",
              emptyText: "sender@example.com",
            },
          ],
        },
      ],
      buttons: [
        {
          text: "Save Host Config",
          iconCls: "fas fa-save",
          handler: "onSaveHostConfig",
        },
      ],
    },
  ],
});
