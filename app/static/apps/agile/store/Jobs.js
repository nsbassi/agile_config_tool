Ext.define("AgileAcpt.store.Jobs", {
  extend: "Ext.data.Store",
  alias: "store.jobs",
  model: "AgileAcpt.model.Job",
  autoLoad: true,
  proxy: {
    type: "ajax",
    url: "/api/jobs/",
    reader: {
      type: "json",
      rootProperty: "",
    },
    headers: {
      Authorization: "Bearer " + localStorage.getItem("jwt"),
    },
  },
});
