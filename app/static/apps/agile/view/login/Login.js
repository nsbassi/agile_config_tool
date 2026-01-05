Ext.define("AgileAcpt.view.login.Login", {
  extend: "Ext.window.Window",
  xtype: "loginview",
  requires: ["AgileAcpt.controller.Login"],
  controller: "login",
  title: "Agile Configuration Management - Login",
  closable: false,
  resizable: false,
  draggable: false,
  modal: true,
  width: 400,
  bodyPadding: 10,
  layout: "fit",
  items: [
    {
      xtype: "form",
      reference: "loginForm",
      bodyPadding: 10,
      defaults: { xtype: "textfield", anchor: "100%", allowBlank: false },
      items: [
        { fieldLabel: "Username", name: "username" },
        { fieldLabel: "Password", name: "password", inputType: "password" },
      ],
      buttons: [{ text: "Login", formBind: true, handler: "onLoginClick" }],
    },
  ],
});
