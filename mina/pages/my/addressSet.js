//获取应用实例
var commonCityData = require('../../utils/city.js');
var app = getApp();
Page({
    data: {
        provinces: [],
        citys: [],
        districts: [],
        selProvince: '请选择',
        selCity: '请选择',
        selDistrict: '请选择',
        selProvinceIndex: 0,
        selCityIndex: 0,
        selDistrictIndex: 0
    },
    onLoad: function (e) {
        var that = this;
        that.setData({
            id: e.id
        });
        this.initCityData(1);
    },
    onShow: function(e){
      this.getInfo();
    },
    //初始化城市数据
    initCityData:function( level, obj ){
        if (level == 1) {
            var pinkArray = [];
            for (var i = 0; i < commonCityData.cityData.length; i++) {
                pinkArray.push(commonCityData.cityData[i].name);
            }
            this.setData({
                provinces: pinkArray
            });
        } else if (level == 2) {
            var pinkArray = [];
            var dataArray = obj.cityList
            for (var i = 0; i < dataArray.length; i++) {
                pinkArray.push(dataArray[i].name);
            }
            this.setData({
                citys: pinkArray
            });
        } else if (level == 3) {
            var pinkArray = [];
            var dataArray = obj.districtList
            for (var i = 0; i < dataArray.length; i++) {
                pinkArray.push(dataArray[i].name);
            }
            this.setData({
                districts: pinkArray
            });
        }
    },
    bindPickerProvinceChange: function (event) {
        var selIterm = commonCityData.cityData[event.detail.value];
        this.setData({
            selProvince: selIterm.name,
            selProvinceIndex: event.detail.value,
            selCity: '请选择',
            selCityIndex: 0,
            selDistrict: '请选择',
            selDistrictIndex: 0
        });
        this.initCityData(2, selIterm);
    },
    bindPickerCityChange: function (event) {
        var selIterm = commonCityData.cityData[this.data.selProvinceIndex].cityList[event.detail.value];
        this.setData({
            selCity: selIterm.name,
            selCityIndex: event.detail.value,
            selDistrict: '请选择',
            selDistrictIndex: 0
        });
        this.initCityData(3, selIterm);
    },
    bindPickerChange: function (event) {
        var selIterm = commonCityData.cityData[this.data.selProvinceIndex].cityList[this.data.selCityIndex].districtList[event.detail.value];
        if (selIterm && selIterm.name && event.detail.value) {
            this.setData({
                selDistrict: selIterm.name,
                selDistrictIndex: event.detail.value
            })
        }
    },
    bindCancel: function () {
        wx.navigateBack({});
    },
    // 添加、编辑收货地址
    bindSave: function (e) {
        var that = this;
        // 获取表单里name字段值——姓名、手机号、具体地址
        var nickname = e.detail.value.nickname;
        var mobile = e.detail.value.mobile;
        var address = e.detail.value.address;
        if (nickname == ""){
            app.tip({"content": "请填写联系人姓名~~"});
            return;
        }
        if (mobile == "" || !this.isMobile(mobile)){
            app.tip({"content": "请填写有效手机号码~~"});
            return;
        }

        if (that.data.selProvince == "请选择"){
            app.tip({"content": "请选择省或直辖市~~"});
            return;
        }
        if (that.data.selCity == "请选择"){
            app.tip({"content": "请选择城市或区~~"});
            return;
        }
        var city_id = commonCityData.cityData[that.data.selProvinceIndex].cityList[that.data.selCityIndex].id;
        var district_id;
        if (that.data.selDistrict == "请选择" || !that.data.selDistrict) {
            district_id = 0;
        }else{
            district_id = commonCityData.cityData[that.data.selProvinceIndex].cityList[that.data.selCityIndex].districtList[that.data.selDistrictIndex].id;
        }

        if (address == ""){
            app.tip({"content": "请填写具体地址~~"});
            return;
        }

        wx.request({
            url: app.buildUrl("/my/address/set"),
            header: app.getRequestHeader(),
            method: "POST",
            data: {
                id: that.data.id,
                nickname: nickname,
                mobile: mobile,
                province_id: commonCityData.cityData[that.data.selProvinceIndex].id,
                province_str: that.data.selProvince,
                province_index: that.data.selProvinceIndex,
                city_id: city_id,
                city_str: that.data.selCity,
                city_index: that.data.selCityIndex,
                district_id: district_id,
                district_str: that.data.selDistrict,
                district_index: that.data.selDistrictIndex,
                address: address
            },

            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({"content": resp.msg});
                    return;
                }

                // 跳转(返回)
                wx.navigateBack({});
            }

        });

    },
    deleteAddress: function (e) {
    },
    // 获取收货地址信息
    getInfo: function(){
        var that = this;
        if (that.data.id < 1) {
            return;
        }
        wx.request({
            url: app.buildUrl("/my/address/info"),
            header: app.getRequestHeader(),
            data: {
                id: that.data.id
            },
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({"content": resp.msg});
                    return;
                }
                var info = resp.data.info;
                that.setData({
                    info: info,
                    selProvince: info.province_str ? info.province_str : "请选择",
                    selProvinceIndex: info.province_index,
                    selCity: info.city_str ? info.city_str : "请选择",
                    selCityIndex: info.city_index,
                    selDistrict: info.area_str ? info.area_str : "请选择",
                    selDistrictIndex: info.area_index
                });
            }
        });
    },
    // 验证手机号合法性
    isMobile(str) {
        var myreg=/^[1][3-9]\d{9}$|^([6|9])\d{7}$|^[0][9]\d{8}$|^[6]([8|6])\d{5}$/;
        if (!myreg.test(str)) {
            return false;
        } else {
            return true;
        }
    }
});
