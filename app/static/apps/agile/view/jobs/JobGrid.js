Ext.define('AgileAcpt.view.jobs.JobGrid', {
    extend: 'Ext.grid.Panel',
    xtype: 'job-grid',
    requires: ['AgileAcpt.store.Jobs', 'AgileAcpt.controller.Job'],
    controller: 'job',
    store: { type: 'jobs' },
    selModel: 'rowmodel',
    columns: [
        { text: 'ID', dataIndex: 'id', flex: 2 },
        { text: 'Type', dataIndex: 'type', flex: 1 },
        { text: 'Status', dataIndex: 'status', flex: 1 },
        { text: 'Created', dataIndex: 'createdAt', xtype: 'datecolumn', format: 'Y-m-d H:i:s', flex: 1 },
        { text: 'Finished', dataIndex: 'finishedAt', xtype: 'datecolumn', format: 'Y-m-d H:i:s', flex: 1 },
        { text: 'Summary', dataIndex: 'summary', flex: 2 }
    ],
    tbar: [
        { text: 'Refresh', handler: 'onRefreshJobs' },
        { text: 'View Log', handler: 'onViewJobLog' },
        { text: 'Download Output', handler: 'onDownloadOutput' }
    ]
});
