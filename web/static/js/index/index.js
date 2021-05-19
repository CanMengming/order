;
var dashboard_index_ops = {
    init: function () {
        this.drawChart();
    },
    drawChart: function () {
        charts_ops.setOption();
        $.ajax({
            url: common_ops.buildUrl("/chart/dashboard"),
            dataType: 'json',
            success: function (res) {
                charts_ops.drawLine($("#member_order"), res.data, "近30天全站销售统计");
            }
        });

        $.ajax({
            url: common_ops.buildUrl("/chart/finance"),
            dataType: 'json',
            success: function (res) {
                charts_ops.drawLine($("#finance"), res.data, "近30天全站营收统计");
            }
        });
    }
};

$(document).ready(function () {
    dashboard_index_ops.init();
});