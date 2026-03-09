/*----------------------------------------------------------------------------*
 * 瓒崇悆鍗曞満澶嶅紡閫夊彿椤甸潰                                                       *
 *----------------------------------------------------------------------------*/

/* LineSelector 鍖楀崟琛岄夋嫨鍣
------------------------------------------------------------------------------*/
Class('LineSelector', {

    index: function(config) {

        this.vsLine = config.tr;
        this.vsIndex = config.vsIndex;
        this.vsOptions = config.vsOptions;
        this.vsCheckAll = config.vsCheckAll;
        this.spTag = config.spTag;
        this.vsInfo = config.vsInfo;

        this.disabled = this.vsInfo.disabled === 'yes';
        this.index = this.vsInfo.index;
        this.data = []; //鏈琛岀殑鎶曟敞缁撴灉
        this.codeValIdx = Class.config('codeValueIndex');

        this.scm = []; //棣栨℃湯

        this.bindEvent();
        if (this.disabled && !Class.config('stopSale')) {
            this.vsIndex.disabled = true;
        }
        this.vsIndex.checked = true;
        !this.disabled && this.initClearAll(); //鍒濆嬫椂鍏ㄤ笉閫変腑

        // 鍙栨秷鏌愪竴閫夐」鐨勯夋嫨
        this.onMsg('msg_touzhu_cancel', function(line_index, ck_value) {
            if (this.index == line_index) {
                var ck_index, ck;
                ck_index = this.getIndex(Class.config('codeValue'), ck_value);
                ck = this.vsOptions[ck_index].getElementsByTagName('input')[0];
                this.unCheck(ck);
                return false; //鍋滄㈡秷鎭浼犻
            }
        });

    },

    // 缁戝畾鐩稿叧浜嬩欢
    bindEvent: function() {
        var Y = this;

        // 榧犳爣缁忚繃姣忎竴琛屾椂鏀瑰彉鏍峰紡
        this.get(this.vsLine).hover(function() {
            this.style.backgroundColor = '#FEFFD1';
        }, function() {
            this.style.backgroundColor = '';
        });

        // 鐐瑰嚮闅愯棌鏌愬満姣旇禌
        this.vsIndex.onclick = function() {
            Y.hideLine();
        }

        if (this.disabled) return;

        // 鐐瑰嚮閫夐」杩涜屾姇娉
        for (var i = 0, l = this.vsOptions.length; i < l; i++) {
            this.vsOptions[i].parentNode.onmousedown = function() {
                var ck = this.getElementsByTagName('input')[0];
                ck.checked ? Y.unCheck(ck) : Y.check(ck);
            }
        }

        // 鍏ㄩ/鍏ㄤ笉閫
        this.vsCheckAll.parentNode.onmousedown = function() {
            var ck = this.getElementsByTagName('input')[0];
            ck.checked = !ck.checked;
            ck.checked ? Y.checkAll() : Y.clearAll();
        }
    },

    check: function(ck) {
        this.data[this.codeValIdx[ck.value]] = ck.value;
        ck.checked = true;
        this.scm.remove(ck.value);
        this.scm.push(ck.value);
        ck.parentNode.parentNode.style.backgroundColor = '#FFDAA4';
        this.vsCheckAll.checked = this.getData().length == this.vsOptions.length;
        this.changed();
    },

    unCheck: function(ck) {
        this.data[this.codeValIdx[ck.value]] = undefined;
        ck.checked = false;
        this.scm.remove(ck.value);
        ck.parentNode.parentNode.style.backgroundColor = '';
        this.vsCheckAll.checked && (this.vsCheckAll.checked = false);
        this.changed();
    },

    checkAll: function() {
        this.data = Class.config('codeValue').slice();
        this.vsCheckAll.checked = true;
        this.scm = [];
        for (var i = 0, l = this.vsOptions.length; i < l; i++) {
            var input = this.vsOptions[i].getElementsByTagName('input')[0];
            if (!input.checked) {
                input.checked = true;
                this.vsOptions[i].parentNode.style.backgroundColor = '#FFDAA4';
            }
            this.scm.push(input.value);
        }
        this.changed();
    },

    clearAll: function() {
        this.data = [];
        this.vsCheckAll.checked = false;
        for (var i = 0, l = this.vsOptions.length; i < l; i++) {
            this.vsOptions[i].getElementsByTagName('input')[0].checked = false;
            this.vsOptions[i].parentNode.style.backgroundColor = '';
        }
        this.scm = [];
        this.changed();
    },

    initClearAll: function() {
        var ck = this.vsLine.getElementsByTagName('input');
        for (var i = 1, l = ck.length; i < l; i++) {
            ck[i].checked = false;
        }
    },

    hideLine: function() { //闅愯棌褰撳墠琛
        if (this.vsLine.style.display != 'none') {
            this.vsLine.style.display = 'none';
            this.getData().length > 0 && this.clearAll();
            !this.vsIndex.disabled && this.postMsg('msg_one_match_hided');
            Y.C('autoHeight') && this.postMsg('msg_update_iframe_height');
        }
    },

    showLine: function() { //鏄剧ず褰撳墠琛
        if (this.vsLine.style.display == 'none') {
            this.vsLine.style.display = '';
            this.vsIndex.checked = true;
            !this.vsIndex.disabled && this.postMsg('msg_one_match_showed');
            Y.C('autoHeight') && this.postMsg('msg_update_iframe_height');
        }
    },

    // 鑾峰彇鏈琛屾姇娉ㄦ暟鎹
    getData: function() {
        if (this.disabled) return [];
        return this.data.each(function(d) {
            d && this.push(d);
        }, []);
    },

    // 閫変腑鏌愪簺鐗瑰畾鐨勯夐」
    checkCertainVsOptions: function(ck_value) {
        var code_value = Class.config('codeValue').slice();
        ck_value.split(',').each(function(v) {
            var i = /^\d$/.test(v) ? v : this.getIndex(code_value, v); //濡傛灉鏄 1,2,3 鐩存帴鐢╲
            var chk = this.vsOptions[i];
            if (chk) {
                this.check(chk.getElementsByTagName('input')[0]);
            }
        }, this);
    },

    // 鏇存柊SP鍊
    updateSP: function(sp_values) {
        if (this.spTag && !this.disabled) {
            this.spTag.each(function(item, index) {
                var sp_old, sp_new, arrow = '';
                sp_old = parseFloat(item.innerHTML);
                sp_new = parseFloat(sp_values[index]);
                this.get(item).removeClass('red').removeClass('green');
                if (sp_new > sp_old) {
                    this.get(item).addClass('red');
                    arrow = '鈫';
                } else if (sp_new < sp_old) {
                    this.get(item).addClass('green');
                    arrow = '鈫';
                }
                if (Class.config('playName') == 'jq' || Class.config('playName') == 'bq') {
                    arrow = ''; //杩涚悆鍜屽崐鍏ㄤ笉鏄剧ず绠澶
                }
                item.innerHTML = sp_new ? sp_new.toFixed(2) + arrow : '--';
            }, this);
        }
    },

    changed: function() {
        this.postMsg('msg_line_selector_changed');
    }

});


/* TableSelector 鍖楀崟瀵归樀鍒楄〃閫夋嫨鍣
------------------------------------------------------------------------------*/
Class('TableSelector', {

    vsInfo: [],
    hiddenMatchesNum: 0,
    codes: [],

    index: function(config) {
        var Y = this;

        this.vsTable = this.need(config.vsTable);
        if (Class.config('playName') == 'rqspf') {
            this.ckRangqiu = this.need(config.ckRangqiu);
            this.ckNoRangqiu = this.need(config.ckNoRangqiu);
        }
        this.ckOutOfDate = this.need(config.ckOutOfDate);
        this.hiddenMatchesNumTag = this.need(config.hiddenMatchesNumTag);
        this.matchShowTag = this.need(config.matchShowTag);
        this.matchFilter = this.need(config.matchFilter);
        this.leagueShowTag = this.need(config.leagueShowTag);
        this.leagueSelector = this.need(config.leagueSelector);
        this.selectAllLeague = this.need(config.selectAllLeague);
        this.selectOppositeLeague = this.need(config.selectOppositeLeague);

        this.stopSale = Class.config('stopSale');
        this.allEnd = this.get('#out_of_date_matches').val() == this.get('#all_matches').val(); //鍏ㄩ儴鎴姝

        this.initVsTrs(config.vsLines); //寤虹珛濂藉悇涓鍗曡屽硅薄

        this.onMsg('msg_line_selector_changed', this.changed);

        this.onMsg('msg_touzhu_line_cancel', function(index) {
            this.vsTrs[index - 1].clearAll();
        });

        this.onMsg('msg_get_touzhu_codes', function() {
            return this.codes;
        });

        this.onMsg('msg_get_codes_4_submit', function() {
            return this.getCodes4Submit();
        });

        // 涓烘樉绀哄栭噾棰勬祴鎻愪緵鐩稿叧鏁版嵁
        this.onMsg('msg_get_data_4_prize_predict', function() {
            return this.getData4PrizePredict();
        });

        // 杩斿洖淇鏀规椂閲嶇幇涔嬪墠閫夋嫨鐨勬瘮璧
        this.onMsg('msg_restore_codes', function(codes) {
            this.restoreCodes(codes);
        });

        // 鏄剧ずfid姣旇禌
        this.onMsg('msg_filter_fid', function(fids) {
            this.showFidMatches(fids);
        });

        this.initMatchFilter(); //璧涗簨杩囨护

        if (this.stopSale == false && !Y.C('autoHeight')) {
            setTimeout(function() { Y.updateSP() }, 30000); //鏇存柊SP鍊(椤甸潰杞藉叆鍚30绉)
        }
    },

    initVsTrs: function(vs_lines) {
        var Y = this,
            input_length = 0;
        //vsTrs 鏄鍗曡岀殑yclass瀵硅薄
        this.vsTrs = this.need(vs_lines).each(function(tr, i) {
            var vs_info = Y.dejson(tr.getAttribute('value'));
            input_length == 0 && (input_length = tr.getElementsByTagName('input').length);
            this[i] = Y.lib.LineSelector({
                tr: tr,
                vsIndex: tr.getElementsByTagName('input')[0],
                vsOptions: tr.getElementsByTagName('label'),
                vsCheckAll: tr.getElementsByTagName('input')[input_length - 1],
                spTag: Y.get('span.sp_value', tr),
                vsInfo: vs_info
            });
            Y.vsInfo[vs_info.index] = vs_info; //瀛樺偍鎵鏈夋瘮璧涚殑鐩稿叧鏁版嵁
        }, []);
    },

    // 鑾峰彇鎵鏈夎岀殑鎶曟敞鏁版嵁
    getCodes: function() {
        this.codes = this.vsTrs.each(function(item) {
            if (item.disabled) return;
            var _data = item.getData();
            if (_data.length > 0) {
                this.push({
                    'index': item.index,
                    'arr': _data,
                    'dan': false,
                    'vsInfo': item.vsInfo,
                    'scm': item.scm //棣栨℃湯
                });
            }
        }, []);
        return this.codes;
    },

    // 鑾峰彇鎶曟敞鏁版嵁(鐢ㄤ簬鎻愪氦鏃)
    // {'codes':'2:[鑳淽/5:[璐焆/6:[鑳,骞,璐焆', 'danma':'2:[鑳淽'}
    getCodes4Submit: function() {
        var codes, codes2, danma, arr_danma, tuo;
        codes = new Array();
        codes2 = new Array(); //杩囨护
        tuo = new Array(); //鍙风爜绡
        danma = new Array();
        arr_danma = this.postMsg('msg_get_danma').data;
        this.vsTrs.each(function(item) {
            var i, v, scm;
            v = item.getData();
            i = item.index;
            scm = item.scm;
            if (v.length > 0) {
                var tmp_code = '',
                    t2;
                t2 = tmp_code = i + ':[';
                tmp_code += v.each(function(v2) {
                    this.push(v2);
                }, []).join(',');
                tmp_code += ']';
                codes.push(tmp_code);
                if (!scm) {
                    scm = [];
                }
                codes2.push(t2 + scm.join(',') + ']');
                if (arr_danma[i]) {
                    danma.push(tmp_code);
                } else {
                    tuo.push(tmp_code)
                }
            }
        });
        return { 'codes': codes.join('/'), 'danma': danma.join('/'), 'codes2': codes2.join('/'), 't': tuo.join('/') };
    },

    // 涓烘樉绀哄栭噾棰勬祴鎻愪緵鐩稿叧鏁版嵁
    getData4PrizePredict: function() {
        var Y = this;
        return this.vsTrs.each(function(item, i) {
            var sp = [],
                vs_info;
            if (item.spTag) {
                sp = item.spTag.each(function(item2) {
                    this.push(parseFloat(item2.innerHTML) || 0);
                }, []);
            }
            vs_info = Y.vsInfo[item.index];
            this.push({
                'serialNumber': item.index,
                'lg': vs_info.leagueName,
                'main': vs_info.homeTeam,
                'guest': vs_info.guestTeam,
                'rq': vs_info.rangqiuNum,
                'sp': sp
            });
        }, []);
    },

    changed: function() {
        this.postMsg('msg_table_selector_changed', this.getCodes());
    },

    initMatchFilter: function() {
        var Y = this;

        // 鍑犱釜澶嶉夋嗙殑鍒濆嬬姸鎬
        if (Class.config('playName') == 'rqspf') {
            this.ckRangqiu.prop('checked', true);
            this.get('#rangqiu_tag').html(this.get('#rangqiu_matches').val());
            this.ckNoRangqiu.prop('checked', true);
            this.get('#no_rangqiu_tag').html(this.get('#no_rangqiu_matches').val());
        }
        this.ckOutOfDate.prop('checked', false);
        this.get('#out_of_date_tag').html(this.get('#out_of_date_matches').val() + '鍦');

        this.initVsDisplay(); //鍒濆嬪寲瀵归樀鐨勬樉绀烘儏鍐

        this.onMsg('msg_update_hidden_matches_num', function() {
            Y.hiddenMatchesNumTag.html(Y.hiddenMatchesNum);
        });

        // 璁惧畾娑堟伅锛屼互鏀瑰彉闅愯棌姣旇禌鏁伴噺鐨勬樉绀
        this.onMsg('msg_one_match_showed', function() {
            Y.hiddenMatchesNum--;
            Y.postMsg('msg_update_hidden_matches_num');
        });
        this.onMsg('msg_one_match_hided', function() {
            Y.hiddenMatchesNum++;
            Y.postMsg('msg_update_hidden_matches_num');
        });

        this.onMsg('msg_show_certain_league', function(league_name) {
            Y.showCertainLeague(league_name);
        });

        // 鎴愬潡鍦版樉绀烘垨闅愯棌鏌愬綊灞炴棩鏈熶笅鐨勬墍鏈夎禌浜
        this.onMsg('msg_show_or_hide_matches', function(id, obj) {
            if (Y.get(obj).html().indexOf('闅愯棌') != -1) {
                Y.need('#' + id).hide();
                Y.get(obj).html('鏄剧ず<s class="c_down"></s>');
            } else {
                Y.need('#' + id).show();
                Y.get(obj).html('闅愯棌<s class="c_up"></s>');
            }
            Y.C('autoHeight') && this.postMsg('msg_update_iframe_height');
        });

        // 鏄剧ず鎴栭殣钘忔湁璁╃悆鐨勫満娆
        if (Class.config('playName') == 'rqspf') {
            this.ckRangqiu.click(function() {
                var be_controlled = Y.stopSale || Y.ckOutOfDate.prop('checked');
                Y.vsTrs.each(function(item) {
                    if (Y.vsInfo[item.index].rangqiuNum != 0 && (!item.disabled || be_controlled)) {
                        this.checked ? item.showLine() : item.hideLine();
                    }
                }, this);
            });
            // 鏄剧ず鎴栭殣钘忛潪璁╃悆鐨勫満娆
            this.ckNoRangqiu.click(function() {
                var be_controlled = Y.stopSale || Y.ckOutOfDate.prop('checked');
                Y.vsTrs.each(function(item) {
                    if (Y.vsInfo[item.index].rangqiuNum == 0 && (!item.disabled || be_controlled)) {
                        this.checked ? item.showLine() : item.hideLine();
                    }
                }, this);
            });
        }

        // 鏄剧ず鎴栭殣钘忓凡鎴姝㈢殑鍦烘
        this.ckOutOfDate.click(function() {
            var be_controlled = true;
            Y.vsTrs.each(function(item) {
                if (Class.config('playName') == 'rqspf') {
                    be_controlled = (Y.vsInfo[item.index].rangqiuNum != 0 && Y.ckRangqiu.prop('checked')) ||
                        (Y.vsInfo[item.index].rangqiuNum == 0 && Y.ckNoRangqiu.prop('checked'));
                }
                if (item.disabled && be_controlled) {
                    this.checked ? item.showLine() : item.hideLine();
                }
            }, this);
            //this.checked ? Y.showAllTBody() : Y.hideSpareTBody();
            this.checked && Y.showAllTBody();
        });

        // 鐐瑰嚮宸查殣钘忔瘮璧涚殑鏁伴噺鍒欐樉绀烘墍鏈夌殑姣旇禌
        this.hiddenMatchesNumTag.click(function() {
            if (this.innerHTML != '0') {
                Y.showAllMatches();
            }
        });

        // 鏄剧ず鎴栭殣钘忚仈璧涢夋嫨鍖哄煙
        var timeout_id;
        this.leagueShowTag.mouseover(function() {
            if (Y.leagueSelector.one().getElementsByTagName('ul')[0].innerHTML == '') {
                Y.createLeagueList(); //鐢熸垚鑱旇禌閫夋嫨鍒楄〃
            }
            clearTimeout(timeout_id);
            Y.leagueSelector.show();
            Y.leagueShowTag.addClass('ls_h_btn');
        });
        this.leagueShowTag.mouseout(function() {
            timeout_id = setTimeout(function() {
                Y.leagueSelector.hide();
                Y.leagueShowTag.removeClass('ls_h_btn');
            }, 100);
        });
        this.leagueSelector.mouseover(function() {
            clearTimeout(timeout_id);
            Y.leagueSelector.show();
        });
        this.leagueSelector.mouseout(function() {
            timeout_id = setTimeout(function() {
                Y.leagueSelector.hide();
                Y.leagueShowTag.removeClass('ls_h_btn');
            }, 100);
        });

        // 閫夋嫨鎴栭殣钘忔煇涓鎸囧畾鐨勮仈璧
        this.leagueSelector.live('ul input', 'click', function(e, ns) {
            Y.vsTrs.each(function(item) {
                if (Y.vsInfo[item.index].leagueName == this.value &&
                    (!item.disabled || Y.stopSale || Y.ckOutOfDate.prop('checked'))) {
                    this.checked ? item.showLine() : item.hideLine();
                }
            }, this);
        });

        // 鍏ㄩ夋墍鏈夎仈璧
        this.selectAllLeague.click(function() {
            Y.showAllMatches();
        });

        // 鍙嶉夋墍鏈夎仈璧
        this.selectOppositeLeague.click(function() {
            Y.leagueSelector.find('ul input').each(function(item) {
                item.click();
            });
        });

        // 鏄剧ず鎴栭殣钘忚禌浜嬬瓫閫夊尯鍩
        this.matchShowTag.drop(this.matchFilter, {
            y: this.ie ? 7 : -1,
            x: this.ie ? 0 : -1,
            focusCss: 'dc_all_s dc_all_on',
            onshow: function() {
                this.matchShowTag.find('s').swapClass('c_down', 'c_up');
            },
            onhide: function() {
                this.matchShowTag.find('s').swapClass('c_up', 'c_down');
            }
        });

        // 鐐瑰嚮杩涜岃禌浜嬬瓫閫(鍏ㄩ儴姣旇禌銆佺儹闂ㄦ姇娉ㄣ佸畾鑳嗘渶澶...)
        this.matchFilter.find('a').click(function() {
            var _html, _value = Y.get(this).attr('value');
            if (_value == 'all') { //鍏ㄩ儴姣旇禌
                Y.showAllMatches();
                _html = '鍏ㄩ儴姣旇禌';
            } else if (_value == 'hot') { //鐑闂ㄦ姇娉
                if (typeof Y.hotMatches == 'undefined') {
                    var arr_tzbl = [];
                    var obj_tzbl = Y.vsTable.find('.tzbl');
                    obj_tzbl.each(function(item) {
                        var tmp_info = Y.dejson(item.parentNode.getAttribute('value'));
                        if (tmp_info.disabled != 1 || Y.stopSale || Y.allEnd) {
                            if (!parseFloat(item.innerHTML)) return;
                            arr_tzbl.push({ 'index': tmp_info.index, 'percentage': parseFloat(item.innerHTML) });
                        }
                    });
                    Y.hotMatches = [];
                    if (arr_tzbl.length != 0) {
                        arr_tzbl.sort(function(a, b) { return b.percentage - a.percentage; });
                        arr_tzbl.length > 10 && (arr_tzbl = arr_tzbl.slice(0, 10)); //鍙栧墠鍗
                        arr_tzbl.each(function(item) {
                            Y.hotMatches.push(item.index);
                        });
                    }
                }
                Y.showCertainMatches(Y.hotMatches);
                _html = '鐑闂ㄦ姇娉';
            } else if (_value == 'dingdan') { //瀹氳儐鏈澶
                if (typeof Y.dingdanMatches == 'undefined') {
                    Y.ajax({
                        url: 'https://www.500.com/static/500public/xml/long/ssfx/zqdc/tzddcs/' + Class.config('expect') + '.xml',
                        end: function(data) {
                            var dingdan_matches = [];
                            if (data.xml) {
                                Y.qXml('//row', data.xml, function(obj, i) {
                                    if (!Y.vsTrs[obj.items.ordernum - 1].disabled || Y.stopSale || Y.allEnd) {
                                        dingdan_matches.push({ 'index': obj.items.ordernum, 'dingdanNum': obj.items['dingdan_' + obj.items.dingdan_max] });
                                    }
                                });
                            }
                            dingdan_matches.sort(function(a, b) { return b.dingdanNum - a.dingdanNum; });
                            dingdan_matches.length > 10 && (dingdan_matches = dingdan_matches.slice(0, 10)); //鍙栧墠鍗
                            Y.dingdanMatches = [];
                            dingdan_matches.each(function(item) {
                                Y.dingdanMatches.push(item.index);
                            });
                            Y.showCertainMatches(Y.dingdanMatches);
                        }
                    });
                } else {
                    Y.showCertainMatches(Y.dingdanMatches);
                }
                _html = '瀹氳儐鏈澶';
            } else if (_value == 'rank') { //鎺掑悕鐩稿樊10浠ヤ笂
                if (typeof Y.rankMatches == 'undefined') {
                    Y.rankMatches = [];
                    Y.vsTrs.each(function(item) {
                        if (Math.abs(item.vsInfo.homeTeamRank - item.vsInfo.guestTeamRank) >= 10 &&
                            (!item.disabled || Y.stopSale || Y.allEnd)) {
                            Y.rankMatches.push(item.index);
                        }
                    });
                }
                Y.showCertainMatches(Y.rankMatches);
                _html = '鎺掑悕鐩稿樊';
            }
            Y.matchShowTag.html(_html + '<s class="c_up"></s>');
        });

    },

    // 杩斿洖淇鏀规椂閲嶇幇涔嬪墠閫夋嫨鐨勬瘮璧
    restoreCodes: function(codes) {
        codes.each(function(obj) {
            this.vsTrs[obj.index - 1].checkCertainVsOptions(obj.arr);
        }, this);
    },

    // 鏇存柊SP鍊
    updateSP: function() {
        this.ajax({
            url: 'https://www.500.com/static/public/bjdc/xml/sp/just_' + Class.config('expect') + '_' + Class.config('playId') + '.xml',
            end: function(data) {
                var Y = this;
                if (data.xml) {
                    this.qXml('/w/*', data.xml, function(obj, i) {
                        var id = obj.node.nodeName.slice(1);
                        var wid = id - 1 >= 0 ? id - 1 : i;
                        var sp_values = new Array();
                        for (var j = 1, l = Class.config('codeValue').length * 2; j <= l; j += 2) {
                            sp_values.push(obj.items['c' + j]);
                        }
                        this.vsTrs[wid].updateSP(sp_values);
                    });
                    setTimeout(function() { Y.updateSP() }, 5 * 60 * 1000); //姣忛殧涓娈垫椂闂村啀鍙栦竴娆
                } else {
                    setTimeout(function() { Y.updateSP() }, 5000); //澶辫触鍚庣煭鏃堕棿鍐呭啀娆¤锋眰
                }
            }
        });
    },

    // 鏄剧ず鎵鏈夎禌浜
    showAllMatches: function() {
        this.vsTrs.each(function(item) {
            if (!item.disabled || this.stopSale || this.ckOutOfDate.prop('checked')) {
                item.showLine();
            }
        }, this);
        this.leagueSelector.find('ul input').each(function(item) {
            !item.checked && (item.checked = true);
        }, this);
        this.matchShowTag.html('鍏ㄩ儴姣旇禌' + this.matchShowTag.html().substr(4));
        if (Class.config('playName') == 'rqspf') {
            this.ckRangqiu.prop('checked', true);
            this.ckNoRangqiu.prop('checked', true);
        }
    },

    // 鍙鏄剧ず鏌愪釜鐗瑰畾鐨勮仈璧(鐢ㄤ簬璧勮鍖虹殑璺宠浆)
    showCertainLeague: function(league_name) {
        if (!(league_name instanceof Array)) {
            league_name = [league_name];
        }
        this.vsTrs.each(function(item) {
            if (league_name.indexOf(item.vsInfo.leagueName) > -1 && (!item.disabled || this.stopSale || this.allEnd)) {
                item.showLine();
            } else {
                item.hideLine();
            }
        }, this);
        this.createLeagueList();
        this.leagueSelector.find('ul input').each(function(item) {
            item.checked = league_name.indexOf(item.value) > -1;
        }, this);
    },

    // 鍒濆嬪寲瀵归樀鐨勬樉绀烘儏鍐
    initVsDisplay: function() {
        var Y = this;
        var arr_tbody = this.vsTable.find('tbody').filter(function(tBody) {
            return tBody.id && /^\d+-\d+-\d+$/.test(tBody.id)
        });
        if (this.stopSale || this.allEnd) {
            Class.config('disableBtn', true); //姝ゆ椂绂佺敤浠ｈ喘鎴栧悎涔版寜閽
        }
        if (this.stopSale == true) {
            this.ckOutOfDate.prop('checked', true);
            this.ckOutOfDate.prop('disabled', true);
        } else if (this.allEnd) {
            this.ckOutOfDate.prop('checked', true);
            this.ckOutOfDate.prop('disabled', true);
            this.showAllMatches();
        } else {
            arr_tbody.nodes.each(function(item, index) {
                if (this.get(item).getSize().offsetHeight == 0) {
                    document.getElementById('switch_for_' + item.id).getElementsByTagName('a')[0].style.visibility = 'hidden';
                    //	this.get('#switch_for_' + item.id).parent('tbody').hide(); //鍏朵粬褰掑睘鏃ユ湡涓嬫墍鏈夌殑姣旇禌鍧囨埅姝㈡椂锛岃tbody鍚屾牱瑕侀殣钘
                }
            }, this);
        }
    },

    // 鏄剧ず鎵鏈夌殑tbody
    showAllTBody: function() {
        this.get('tbody', this.vsTable).show();
    },

    // 鏄剧ず鐗瑰畾鐨勪竴浜涙瘮璧
    showCertainMatches: function(arr_matches) {
        this.vsTrs.each(function(item) {
            this.getIndex(arr_matches, item.index) !== -1 ? item.showLine() : item.hideLine();
        }, this);
    },

    // 鏄剧ず鎸囧畾fid鐨勬瘮璧
    showFidMatches: function(fids) {
        this.vsTrs.each(function(item) {
            fids.indexOf(item.vsLine.getAttribute('fid')) !== -1 ? item.showLine() : item.hideLine();
        }, this);
    },

    // 鐢熸垚鑱旇禌閫夋嫨鍒楄〃
    createLeagueList: function() {
        var Y = this;
        var arr_league = [];
        var league_list_html = '';
        var match_num_of_league = {};
        Y.vsTrs.each(function(item) {
            var league_name = Y.vsInfo[item.index].leagueName;
            if (!item.disabled || Y.stopSale || Y.allEnd) {
                if (arr_league.indexOf(league_name) == -1) {
                    arr_league.push(league_name);
                    league_list_html += '<li><label><input type="checkbox" class="chbox" checked="checked" value="' + league_name + '" /><span style="padding:2px 4px;color:#FFF;background:' + Y.vsInfo[item.index].bgColor + '">' + league_name + '</span>[' + league_name + '_num]</label></li>';
                }
                if (typeof match_num_of_league[league_name] == 'undefined') {
                    match_num_of_league[league_name] = 1;
                } else {
                    match_num_of_league[league_name]++;
                }
            }
        });
        for (var league_name in match_num_of_league) {
            league_list_html = league_list_html.replace(league_name + '_num', match_num_of_league[league_name]);
        }
        Y.get(league_list_html).insert(Y.leagueSelector.find('ul'));
    }

});


/* TouzhuInfo 鍖楀崟鎶曟敞淇℃伅(涓琛)
------------------------------------------------------------------------------*/
Class('TouzhuInfoLine', {

    index: function(config) {
        this.index = config.index;
        this.homeTeam = config.homeTeam;
        this.guestTeam = config.guestTeam;
        this.endTime = config.endTime;

        // 鎺ユ敹娑堟伅锛岀敓鎴愭煇鏉＄壒瀹氱殑鎶曟敞淇℃伅
        this.onMsg('msg_get_tr_html', function(oTr) {
            if (oTr.index == this.index) {
                return this.createTrHtml(oTr);
            }
        });

        // 鎺ユ敹娑堟伅锛岃繑鍥炲崟鍦烘瘮璧涚殑鎴姝㈡椂闂
        this.onMsg('msg_get_endtime', function(line_index) {
            if (line_index == this.index) {
                return this.endTime;
            }
        });
    },

    // 鐢熸垚涓琛屾姇娉ㄤ俊鎭鐨刪tml
    createTrHtml: function(oTr) {
        var tr_html, td_html, play_name, danma;
        td_html = '';
        play_name = Class.config('playName');
        oTr.arr.each(function(v) {
            td_html += '<span class="' + (play_name == 'jq' ? 'x_sz' : 'x_s') + '" value="' + this.index + '|' + v + '">' + v + '</span>';
        }, this);
        danma = this.postMsg('msg_get_danma').data;
        if (play_name == 'rqspf') {
            tr_html = '<tr>' +
                '<td>' +
                '<input type="checkbox" class="chbox" checked="checked" onclick="Yobj.postMsg(\'msg_touzhu_line_cancel\', ' + this.index + ')" />' +
                '<span class="chnum">' + this.index + '</span>' +
                '</td>' +
                '<td class="t1" title="' + this.homeTeam + ' (' + oTr.vsInfo.rangqiuNum + ') ' + this.guestTeam + '">' + this.homeTeam + '</td>' +
                '<td class="t1">' + td_html + '</td>' +
                '<td><input type="checkbox" class="dan" value="' + this.index + '"' + (danma[this.index] ? ' checked="checked"' : '') + ' />' +
                '</tr>';
        } else {
            tr_html = '<tr>' +
                '<td>' +
                '<input type="checkbox" class="chbox" checked="checked" onclick="Yobj.postMsg(\'msg_touzhu_line_cancel\', ' + this.index + ')" />' +
                '<span class="chnum">' + this.index + '</span>' +
                '</td>' +
                '<td>' + this.homeTeam + '<span class="sp_vs">VS</span>' + this.guestTeam + '</td>' +
                '<td><input type="checkbox" class="dan" value="' + this.index + '"' + (danma[this.index] ? ' checked="checked"' : '') + ' />' +
                '</tr>' +
                '<tr>' +
                '<td colspan="3">' + td_html + '</td>' +
                '</tr>';
        }
        return tr_html;
    }

});


/* TouzhuInfo 鍖楀崟鎶曟敞淇℃伅
------------------------------------------------------------------------------*/
Class('TouzhuInfo', {

    matchNum: 0,
    danma: {},
    danmaNum: 0,

    index: function(config) {
        var Y = this;

        this.endtime = this.get(config.endtime);
        this.touzhuTable = this.need(config.touzhuTable);
        this.touzhuTrs = this.need(config.vsLines).each(function(tr, i) {
            var vs_info = Y.dejson(tr.getAttribute('value'));
            this[i] = Y.lib.TouzhuInfoLine(vs_info);
        }, []);

        // 鎺ユ敹娑堟伅锛屾洿鏂版姇娉ㄤ俊鎭
        this.onMsg('msg_table_selector_changed', function(data) {
            this.updateTouzhuInfoArea(data);
            //this.matchNum == this.danmaNum ? this.disableOrEnableDanma(-2) : this.storeDanma();
            this.storeDanma();
            //this.danmaNum == 0 && this.disableOrEnableDanma(-2);
            if (this.danmaNum == this.matchNum) { //鏇存柊鍚庡綋鑳嗙爜鏁颁笌鍦烘℃暟鐩哥瓑鏃讹紝娓呯┖鑳嗙爜
                this.disableOrEnableDanma(-1);
                this.storeDanma();
            }
            this.changed();
        });

        this.onMsg('msg_get_danma', function() {
            return this.danma;
        });

        // 绂佺敤鎴栨仮澶嶈儐鐮佸嶉夋
        this.onMsg('msg_disable_or_enable_danma', function(gg_match_num) {
            this.disableOrEnableDanma(gg_match_num);
        });

        this.spanCss = Class.config('playName') == 'jq' ? 'x_sz' : 'x_s';

        // 榧犳爣缁忚繃鏃舵樉绀轰竴妯绾
        this.touzhuTable.live('span.' + Y.spanCss, 'mouseover', function(e, _y) {
            _y.get(this).addClass(config.mouseoverClass);
        }).live('span.' + Y.spanCss, 'mouseout', function(e, _y) {
            _y.get(this).removeClass(config.mouseoverClass);
        });

        // 鐐瑰嚮鍙栨秷閫夋嫨
        this.touzhuTable.live('span.' + Y.spanCss, 'click', function(e, _y) {
            var a = _y.get(this).attr('value').split('|');
            _y.postMsg('msg_touzhu_cancel', a[0], a[1])
        });

        // 鐐瑰嚮鑳嗙爜鏃
        this.touzhuTable.live('input.dan', 'click', function() {
            Y.storeDanma();
            Y.postMsg('msg_disable_or_enable_ggck', Y.danmaNum);
        });

        // 杩斿洖淇鏀规椂閲嶇幇涔嬪墠閫夋嫨鐨勮儐鐮
        this.onMsg('msg_restore_danma', function(danma) {
            this.touzhuTable.find('input.dan').each(function(item) {
                if (this.getIndex(danma, item.value) !== -1) {
                    this.get(item).prop('checked', true);
                }
            }, this);
            this.storeDanma();
            this.postMsg('msg_disable_or_enable_ggck', this.danmaNum);
        });

    },

    // 鏇存柊鎶曟敞淇℃伅鍖哄煙, 杩斿洖鎵閫夋瘮璧涚殑鏁伴噺
    updateTouzhuInfoArea: function(data) {
        var Y, earliest_endtime, match_num;
        Y = this;
        earliest_endtime = '2099-12-31 00:00';
        match_num = 0;
        this.endtime.html('');
        this.touzhuTable.empty();
        data.each(function(item) {
            var endtime = Y.postMsg('msg_get_endtime', item.index).data;
            endtime < earliest_endtime && (earliest_endtime = endtime); //鍙栧緱鏈鏃╂埅姝㈡椂闂

            var tr = Y.postMsg('msg_get_tr_html', item).data; // 鍙戦佹秷鎭锛岃幏鍙栫敓鎴愯岀殑html
            Y.get(tr).insert(Y.touzhuTable).data('scm', item.scm);
            match_num++;
        });
        earliest_endtime != '2099-12-31 00:00' && Y.endtime.html(earliest_endtime);
        this.matchNum = match_num;
    },

    // 鑾峰彇鑳嗙爜
    storeDanma: function() {
        this.danma = {};
        this.danmaNum = 0;
        this.touzhuTable.find('input.dan').each(function(item) {
            this.danma[item.value] = item.checked;
            this.danma[item.value] && this.danmaNum++;
        }, this);
    },

    disableOrEnableDanma: function(gg_match_num) {
        this.touzhuTable.find('input.dan').each(function(item) {
            if (gg_match_num == -1) { //娓呴櫎鑳嗙爜閫夋嫨
                item.disabled = false;
                this.get(item).prop('checked', false);
            } else if (gg_match_num == -2) { //绂佺敤鎵鏈夎儐鐮
                item.disabled = true;
                this.get(item).prop('checked', false);
            } else if (gg_match_num == 0 || this.danmaNum < gg_match_num - 1) { //鎭㈠嶈儐鐮
                if (!item.checked && !item.disabled) {
                    return;
                }
                item.disabled = false;
            } else { //绂佺敤鏈閫変腑鐨勮儐鐮
                !item.checked && (item.disabled = true);
            }
            this.storeDanma();
        }, this);
    },

    changed: function() {
        this.postMsg('msg_touzhu_info_changed', this.matchNum, this.danmaNum);
    }

});


/* GuoGuan 鍖楀崟杩囧叧淇℃伅
------------------------------------------------------------------------------*/
Class('GuoGuan', {

    ggType: '鑷鐢辫繃鍏',

    ggTypeMap: { '鑷鐢辫繃鍏': 3, '澶氫覆杩囧叧': 2 },
    ggTypeMap2: { 3: '鑷鐢辫繃鍏', 2: '澶氫覆杩囧叧' },

    ggGroup: [
        [],
        ['鍗曞叧'],
        ['2涓1', '2涓3'],
        ['3涓1', '3涓4', '3涓7'],
        ['4涓1', '4涓5', '4涓11', '4涓15'],
        ['5涓1', '5涓6', '5涓16', '5涓26', '5涓31'],
        ['6涓1', '6涓7', '6涓22', '6涓42', '6涓57', '6涓63'],
        ['7涓1'],
        ['8涓1'],
        ['9涓1'],
        ['10涓1'],
        ['11涓1'],
        ['12涓1'],
        ['13涓1'],
        ['14涓1'],
        ['15涓1']
    ],
    ggGroupMap: { '鍗曞叧': 27, '2涓1': 1, '2涓3': 2, '3涓1': 3, '3涓4': 5, '3涓7': 6, '4涓1': 7, '4涓5': 9, '4涓11': 12, '4涓15': 13, '5涓1': 14, '5涓6': 28, '5涓16': 29, '5涓26': 18, '5涓31': 19, '6涓1': 20, '6涓7': 30, '6涓22': 31, '6涓42': 32, '6涓57': 25, '6涓63': 26, '7涓1': 35, '8涓1': 36, '9涓1': 37, '10涓1': 38, '11涓1': 39, '12涓1': 40, '13涓1': 41, '14涓1': 42, '15涓1': 43 },

    matchNum: 0,
    danmaNum: 0,

    index: function(config) {
        var Y = this;

        this.switchTag = this.need(config.switchTag);
        this.ggTable = this.need(config.ggTable);

        // 鍒囨崲杩囧叧绫诲瀷
        this.switchTag.each(function(item) {
                Y.get(item).click(function() {
                    Y.ggTagSwitched(this);
                })
            }),

            // 褰撴姇娉ㄤ俊鎭鏀瑰彉鏃
            this.onMsg('msg_touzhu_info_changed', function(match_num, danma_num) {
                this.matchNum = match_num;
                this.danmaNum = danma_num;
                this.updateGgInfo();
                this.matchNum == (parseInt(this.getGgInfo()[0]) || 1) && (this.danmaNum = 0);
                this.changed();
                this.disableOrEnableGgCk();
            });

        // 杩斿洖杩囧叧鏂瑰紡
        this.onMsg('msg_get_guoguan_info', function() {
            return this.getGgInfo();
        });

        // 閫夋嫨杩囧叧鏂瑰紡鏃舵洿鏂
        this.ggTable.live('input', 'click', function() {
            Y.changed();
        });

        this.onMsg('msg_update_gg_data', function() {
            Y.changed();
        })

        // 杩斿洖杩囧叧鏂瑰紡
        this.onMsg('msg_get_gg_info_more', function() {
            return this.getGgInfoMore();
        });

        // 绂佺敤鎴栨仮澶嶈繃鍏虫柟寮忛夋嫨妗
        this.onMsg('msg_disable_or_enable_ggck', function(danma_num) {
            this.danmaNum = danma_num;
            this.disableOrEnableGgCk();
            this.changed();
        });

        // 杩斿洖淇鏀规椂閲嶇幇涔嬪墠閫夌殑杩囧叧绫诲瀷
        this.onMsg('msg_restore_gggroup', function(gggroup) {
            this.switchTag.each(function(item) {
                if (this.get(item).attr('value') == this.ggTypeMap2[gggroup]) {
                    this.ggTagSwitched(item);
                }
            }, this);
        });

        // 杩斿洖淇鏀规椂閲嶇幇涔嬪墠閫夌殑杩囧叧鏂瑰紡
        this.onMsg('msg_restore_sgtype', function(sgtype) {
            this.ggTable.find('input').each(function(item) {
                this.getIndex(sgtype, this.ggGroupMap[item.value]) !== -1 && this.get(item).prop('checked', true);
            }, this);
        });

    },

    // 鍒囨崲杩囧叧绫诲瀷鏍囩
    ggTagSwitched: function(obj) {
        this.switchTag.removeClass('an_cur');
        this.get(obj).addClass('an_cur');
        this.ggType = this.get(obj).attr('value');
        this.postMsg('msg_disable_or_enable_danma', -1); //娓呴櫎鑳嗙爜
        this.danmaNum = 0;
        this.updateGgInfo();
        this.changed();
    },

    // 鏇存柊杩囧叧淇℃伅
    updateGgInfo: function() {
        if (this.matchNum == 0) {
            this.ggTable.empty();
            return;
        }

        // 鏍规嵁涓嶅悓鐜╂硶瀵规渶澶т覆鏁板仛闄愬埗
        var max_limit = this.matchNum;
        switch (Class.config('playName')) {
            case 'rqspf':
                this.matchNum > 15 && (max_limit = 15);
                break;
            case 'bf':
                this.matchNum > 3 && (max_limit = 3);
                break;
            case 'jq':
            case 'ds':
            case 'bq':
                this.matchNum > 6 && (max_limit = 6);
        }

        var gg_html, checked_gg_type, checked_html;
        gg_html = checked_html = '';
        checked_gg_type = this.getGgInfo();

        if (this.ggType == '鑷鐢辫繃鍏') {
            for (var i = 1, j = 1; i <= max_limit; i++) {
                if (j % 3 == 1) {
                    if (parseInt(j / 3) % 2 == 1) {
                        gg_html += '<tr class="even">';
                    } else {
                        gg_html += '<tr>';
                    }
                }
                checked_gg_type.each(function(item) {
                    item == this.ggGroup[i][0] && (checked_html = ' checked="checked" ');
                }, this);
                gg_html += '<td class="tl"><label class="mar_l10">' +
                    '<input type="checkbox" class="chbox" name="gg_group"' + checked_html + ' value="' + this.ggGroup[i][0] + '" />' + this.ggGroup[i][0] +
                    '</label></td>';
                if (j++ % 3 == 0) {
                    gg_html += '</tr>';
                }
                checked_html = '';
            }
            Yobj.postMsg('gginfo-change', i > 2);
        } else if (this.ggType == '澶氫覆杩囧叧') {
            for (var i = 1, j = 1; i <= max_limit; i++) { //tr鐨勮緭鍑烘湁bug
                if (this.ggGroup[i].length < 2) {
                    continue;
                }
                if (j % 3 == 1) {
                    if (parseInt(j / 3) % 2 == 1) {
                        gg_html += '<tr class="even">';
                    } else {
                        gg_html += '<tr>';
                    }
                }
                for (var _i = 1, _l = this.ggGroup[i].length; _i < _l; _i++) {
                    checked_gg_type.each(function(item) {
                        item == this.ggGroup[i][_i] && (checked_html = ' checked="checked" ');
                    }, this);
                    gg_html += '<td class="tl"><label class="mar_l10">' +
                        '<input type="radio" class="chbox" name="gg_group"' + checked_html + ' value="' + this.ggGroup[i][_i] + '" />' + this.ggGroup[i][_i] +
                        '</label></td>';
                    if (j++ % 3 == 0) {
                        gg_html += '</tr>';
                    }
                    if (j % 3 == 1) {
                        if (parseInt(j / 3) % 2 == 1) {
                            gg_html += '<tr class="even">';
                        } else {
                            gg_html += '<tr>';
                        }
                    }
                    checked_html = '';
                }
            }
        }
        /* @todo 杩欓噷闇瑕佽ˉ榻愮己灏戠殑鍗曞厓鏍紅d */
        this.ggTable.empty();
        this.get(gg_html).insert(this.ggTable);
    },

    // 鑾峰彇鎵閫夌殑杩囧叧鏂瑰紡
    getGgInfo: function() {
        var gg_info = new Array();
        this.ggTable.find('input').each(function(item) {
            item.checked && gg_info.push(item.value);
        }, this);
        return gg_info;
    },

    // 鑾峰彇鏇翠负瀹屾暣鐨勮繃鍏充俊鎭
    getGgInfoMore: function() {
        var Y, gg_info;
        Y = this;
        gg_info = {};
        gg_info.gggroup = Y.ggTypeMap[Y.ggType];
        gg_info.sgtypename = Y.getGgInfo().join(',');
        gg_info.sgtype = Y.getGgInfo().each(function(item) {
            this.push(Y.ggGroupMap[item]);
        }, []).join(',');
        return gg_info;
    },

    disableOrEnableGgCk: function() {
        this.ggTable.find('input').each(function(item) {
            var gg_match_num = parseInt(item.value) || 1;
            if (gg_match_num <= this.danmaNum) {
                item.disabled = true;
            } else {
                if (!item.disabled) {
                    return;
                }
                item.disabled = false;
            }
        }, this);
    },

    updateGgCk: function() {
        var gg_match_num_real, gg_match_num;
        if (this.danmaNum == this.matchNum - 1) {
            gg_match_num = 1;
        } else if (this.getGgInfo().length == 0) {
            gg_match_num = 0;
        } else {
            gg_match_num_real = parseInt(this.getGgInfo()[0]) || 1;
            if (this.ggType == '鑷鐢辫繃鍏' && gg_match_num_real == this.matchNum) {
                gg_match_num = -2;
                this.danmaNum = 0;
                this.disableOrEnableGgCk();
            } else {
                gg_match_num = gg_match_num_real;
            }
        }
        this.postMsg('msg_disable_or_enable_danma', gg_match_num);
    },

    changed: function() {
        this.updateGgCk();
        this.postMsg('msg_guoguan_info_changed');
    }

});


/* TouzhuResult 鍖楀崟鎶曟敞缁撴灉
------------------------------------------------------------------------------*/
Class('TouzhuResult', {

    beishu: 0,
    matchNum: 0,
    zhushu: 0,
    totalSum: 0,

    index: function(config) {
        var Y = this;

        this.beishuInput = this.need(config.beishuInput);
        this.matchNumTag = this.need(config.matchNum);
        this.zhushuTag = this.need(config.zhushu);
        this.totalSumTag = this.need(config.totalSum);

        this.zhushuCalculator = this.lib.ZhushuCalculator();

        // 鏀瑰彉鍊嶆暟鏃
        this.beishuInput.keyup(function() {
            Y.updateTouzhuResult();
        }).blur(function() {
            if (this.value == '') {
                this.value = 1;
                Y.updateTouzhuResult();
            }
        });

        this.onMsg('msg_guoguan_info_changed', function() {
            this.updateTouzhuResult();
        });

        // 杩斿洖鎶曟敞缁撴灉锛岀敤浜庤〃鍗曟彁浜
        this.onMsg('msg_get_touzhu_result_4_submit', function() {
            return this.getTouzhuResult4Submit();
        });

        // 杩斿洖淇鏀规椂閲嶇幇浣嶆暟
        this.onMsg('msg_restore_beishu', function(beishu) {
            this.beishuInput.val(beishu);
            this.updateTouzhuResult();
        });
    },

    // 鏇存柊鎶曟敞缁撴灉
    updateTouzhuResult: function() {
        if (!parseInt(this.beishuInput.val())) {
            this.beishu = '';
        } else {
            this.beishu = parseInt(this.beishuInput.val());
        }
        this.zhushu = this.countZhushu();
        this.totalSum = this.zhushu * this.beishu * 2;
        this.updateHtml();
    },

    updateHtml: function() {
        this.beishuInput.val(this.beishu); //鏇存柊鍊嶆暟
        this.matchNumTag.html(this.matchNum); //鏇存柊鎵閫夊満娆℃暟
        this.zhushuTag.html(this.zhushu); //鏇存柊娉ㄦ暟
        this.totalSumTag.html(this.totalSum.rmb(true, 0)); //鏇存柊鎶曟敞閲戦
        //	log('閫夊彿鑰楁椂锛' + (new Date - Class.config('d')))
    },

    getTouzhuResult4Submit: function() {
        return {
            zhushu: this.zhushu,
            beishu: this.beishu,
            totalmoney: this.totalSum
        }
    },

    countZhushu: function() { //璁＄畻娉ㄦ暟
        var codes, danma, ggtype, ggmlist;
        codes = this.postMsg('msg_get_touzhu_codes').data;
        this.matchNum = codes.length; //淇濆瓨鍦烘℃暟
        ggmlist = this.postMsg('msg_get_guoguan_info').data;
        if (this.matchNum == 0 || ggmlist.length == 0) {
            return 0;
        }
        ggtype = this.postMsg('msg_get_gg_info_more').data.gggroup;
        danma = this.postMsg('msg_get_danma').data;
        codes.each(function(item) {
            item.dan = danma[item.index];
        });
        return this.postMsg('msg_get_zhushu', codes, ggtype, ggmlist).data;
    }

});


/* Restore 閲嶇幇濉鍐欑殑鏁版嵁
------------------------------------------------------------------------------*/
Class('Restore', {
    hmlParse: { '10': '1:0', '20': '2:0', '21': '2:1', '30': '3:0', '31': '3:1', '32': '3:2', '40': '4:0', '41': '4:1', '42': '4:2', '50': '5:0', '51': '5:1', '52': '5:2', '3A': '鑳滃叾浠', '00': '0:0', '11': '1:1', '22': '2:2', '33': '3:3', '44': '4:4', '1A': '骞冲叾浠', '01': '0:1', '02': '0:2', '12': '1:2', '03': '0:3', '13': '1:3', '23': '2:3', '04': '0:4', '14': '1:4', '24': '2:4', '05': '0:5', '15': '1:5', '25': '2:5', '0A': '璐熷叾浠' },
    bqcParse: { '33': '鑳-鑳', '31': '鑳-骞', '30': '鑳-璐', '13': '骞-鑳', '11': '骞-骞', '10': '骞-璐', '03': '璐-鑳', '01': '璐-骞', '00': '璐-璐' },
    sjb: '涓栨ч,涓栦簹棰,涓栧崡缇庨,涓栧寳缇庨,涓栭潪棰,涓栧ぇ娲嬮'.split(','),
    index: function() {
        var hmlbuy = Y.dejson(Y.get('#codes').val()),
            back = Y.dejson(this.cookie('restore_data'));
        if (back) {
            this.restoreData(back); //杩斿洖淇鏀
        } else if (hmlbuy) { //榛樿ゆ槸姣斿垎
            this.hml = true; //杞鎹㈠瓧绗︽爣璁
            if (hmlbuy.playid == '51') { //鍗婂叏鍦烘槧灏
                this.hmlParse = this.bqcParse;
            } else if (hmlbuy.playid == '42') { //涔熼潪姣斿垎

            } else if (hmlbuy.playid = '34') {
                this.hmlParse = { '3': '鑳', '1': '骞', '0': '璐' };
            } else {
                this.hml = false; //鍏跺畠涓嶈浆鎹
            }
            this.restoreData(hmlbuy); //杩斿洖淇鏀
            if (hmlbuy.matchlist) { //濡傛灉鏈変紶鍏ュ満娆″垪琛锛屾樉绀哄満娆″垪琛
                Yobj.postMsg('msg_filter_fid', hmlbuy.matchlist.split(','));
            }
        } else {
            this.restoreLeague(); //璧勮璺宠浆(鏄剧ず鏌愪竴鑱旇禌)
            this.cookie('bjdc_codes') && this.restoreCodes(); //璧勮璺宠浆(閲嶇幇涔嬪墠鐨勯夋嫨)            
        }
        var me = this;
        this.get('#onlysjb').click(function() { //涓栫晫鏉鎸夐挳
            Yobj.postMsg('msg_show_certain_league', me.sjb);
        });
    },

    restoreData: function(restore_data) {
        //var restore_data = this.dejson(this.cookie('restore_data'));
        this.cookie('restore_data', '', { timeout: -1 });
        this.postMsg('msg_restore_codes', this.processCodes(restore_data.codes));
        this.postMsg('msg_restore_gggroup', restore_data.gggroup);
        if (restore_data.sgtype) {
            this.postMsg('msg_restore_sgtype', restore_data.sgtype.split(','));
        }
        this.postMsg('msg_restore_danma', this.processDanma(restore_data.danma || ''));
        this.postMsg('msg_restore_beishu', restore_data.beishu);
    },

    restoreLeague: function() {
        if (location.href.indexOf('sjb') > -1) { //涓栫晫鏉閾炬帴
            this.postMsg('msg_show_certain_league', this.sjb);
        }
    },

    restoreCodes: function() {
        var codes = decodeURIComponent(this.cookie('bjdc_codes'));
        this.cookie('bjdc_codes', '', { timeout: -1, path: '/' });
        this.postMsg('msg_restore_codes', this.processCodes(codes));
    },

    //2:[骞,璐焆/3:[璐焆 鍙樻垚 [ {index:2, arr:[骞,璐焆}, ... ]
    processCodes: function(codes) {
        var S = this;
        if (codes.trim()) {
            codes = codes.split('/');
            return codes.each(function(item) {
                var info = item.match(/^(\d+):?\[(.+)\]$/);
                var opts = info[2];
                if (S.hml) { //鍏煎瑰彿鐮佺
                    opts = opts.split(',').map(function(v) {
                        return S.hmlParse[v];
                    }).join(',');
                }
                this.push({ 'index': info[1], 'arr': opts });
            }, []);
        } else {
            return [];
        }
    },

    //2:[骞,璐焆/3:[璐焆 鍙樻垚 [2,3]
    processDanma: function(danma) {
        if (danma.length == 0) return '';
        danma = danma.split('/');
        return danma.each(function(item) {
            var info = item.match(/^(\d+):?\[(.+)\]$/);
            this.push(info[1]);
        }, []);
    }

});


/* Clock 褰撳墠鏃堕棿
------------------------------------------------------------------------------*/
Class('Clock', {
    index: function(clock_id) {
        this.clockTag = this.get(clock_id);
        this.runClock();
    },
    runClock: function() {
        var Y = this,
            ini = this.dejson(this.get('#responseJson').val()),
            timebase = +new Date;
        if (ini) {
            timebase = +this.getDate(ini.serverTime)
        }
        setInterval(function() {
            timebase += 1000;
            var d = Y.getDate(timebase);
            var d_str = Y.addZero((d.getMonth() + 1)) + '鏈' + Y.addZero(d.getDate()) + '鏃 ' + Y.addZero(d.getHours()) + ':' + Y.addZero(d.getMinutes()) + ':' + Y.addZero(d.getSeconds());
            Y.clockTag.html(d_str);
        }, 1000);
    },
    addZero: function(n) {
        return parseInt(n) < 10 ? '0' + n : n;
    }
});


/* 涓荤▼搴 ~!@#$%^&*()_+-={}|:"<>?,./;'[]\!!!!!!!!
------------------------------------------------------------------------------*/
Class({

    use: 'mask',
    ready: true,

    index: function() {
        var Y = this,
            d = new Date();

        // 鍒囨崲鏈熷彿
        this.get('#expect_select').change(function() {
            var url = location.href.replace(/#.*/, '');
            if (url.indexOf('expect') != -1) {
                url = url.replace(/expect=.+?(?=&|$)/ig, 'expect=' + this.value.split('|')[0]);
            } else if (url.indexOf('?') != -1 && url.indexOf('=') != -1) {
                url += '&expect=' + this.value.split('|')[0];
            } else {
                url += '?expect=' + this.value.split('|')[0];
            }
            location.replace(url);
        });

        if (this.get('tr.vs_lines').nodes.length == 0) {
            return; //娌″彇鍒板归樀鐨勮瘽鍒欎互涓媕s浠ｇ爜涓嶆墽琛
        }

        Class.extend('getIndex', function(arr, v) {
            for (var i = 0, l = arr.length; i < l; i++) {
                if (arr[i] == v) return i;
            }
            return -1;
        });

        Class.config('playId', parseInt(this.need('#playid').val())); //鐜╂硶id
        Class.config('expect', this.need('#expect').val()); //鏈熷彿
        switch (Class.config('playId')) {
            case 34: //璁╃悆鑳滃钩璐
                Class.config('playName', 'rqspf');
                Class.config('codeValue', ['鑳', '骞', '璐']);
                break;
            case 40: //鎬昏繘鐞冩暟
                Class.config('playName', 'jq');
                Class.config('codeValue', ['0', '1', '2', '3', '4', '5', '6', '7+']);
                break;
            case 41: //涓婁笅鍗曞弻
                Class.config('playName', 'ds');
                Class.config('codeValue', ['涓+鍗', '涓+鍙', '涓+鍗', '涓+鍙']);
                break;
            case 42: //姣斿垎
                Class.config('playName', 'bf');
                Class.config('codeValue', ['鑳滃叾浠', '1:0', '2:0', '2:1', '3:0', '3:1', '3:2', '4:0', '4:1', '4:2',
                    '骞冲叾浠', '0:0', '1:1', '2:2', '3:3',
                    '璐熷叾浠', '0:1', '0:2', '1:2', '0:3', '1:3', '2:3', '0:4', '1:4', '2:4'
                ]);
                break;
            case 51: //鍗婂叏鍦
                Class.config('playName', 'bq');
                Class.config('codeValue', ['鑳-鑳', '鑳-骞', '鑳-璐', '骞-鑳', '骞-骞', '骞-璐', '璐-鑳', '璐-骞', '璐-璐']);
                break;
            default:
        }
        var code_value_index = {};
        Class.config('codeValue').each(function(v, i) {
            code_value_index[v] = i;
        })
        Class.config('codeValueIndex', code_value_index);
        Class.config('stopSale', this.need('#stop_sale').val() == 'yes');

        var tableSelectorClass = this.lib.TableSelector_BF || this.lib.TableSelector;
        tableSelectorClass({
            vsTable: '#vs_table',
            vsLines: 'tr.vs_lines',
            spLines: 'tr.sp_lines',

            ckRangqiu: '#ck_rangqiu',
            ckNoRangqiu: '#ck_no_rangqiu',
            ckOutOfDate: '#ck_out_of_date',
            hiddenMatchesNumTag: '#hidden_matches_num',
            matchShowTag: '#match_show',
            matchFilter: '#match_filter',
            leagueShowTag: '#league_show',
            leagueSelector: '#league_selector',
            selectAllLeague: '#select_all_league',
            selectOppositeLeague: '#select_opposite_league'
        });

        this.lib.TouzhuInfo({
            endtime: '#endtime',
            vsLines: 'tr.vs_lines',
            touzhuTable: '#touzhu_table',
            mouseoverClass: 'nx_s'
        });

        this.lib.GuoGuan({
            switchTag: '#gg_type li',
            ggTable: '#gg_table tbody'
        });

        this.lib.TouzhuResult({
            beishuInput: '#beishu_input',
            matchNum: '#match_num',
            zhushu: '#zhushu',
            totalSum: '#total_sum'
        });

        this.lib.ConfirmForm();
        this.lib.Restore();
        this.lib.Clock('#running_clock');
        this.lib.PrizePredict();
        // 鍒囨崲骞冲潎璧旂巼涓庢姇娉ㄦ瘮渚
        if (Class.config('playName') == 'rqspf') {
            Y.need('#vs_table_header select').change(function() {
                Y.need('#vs_table .pjoz, #vs_table .tzbl, #vs_table .asianhand').hide();
                switch (this.value) {
                    case '0':
                        Y.need('#vs_table .pjoz').show(true, 'inline-block');
                        break;
                    case '1':
                        Y.need('#vs_table .tzbl').show(true, 'inline-block');
                        break;
                    case '2':
                        Y.need('#vs_table .asianhand').show(true, 'inline-block');
                }
            });
        }
        if (Class.config('disableBtn')) { //绂佺敤浠ｈ喘鍜屽悎涔版寜閽
            //Y.get('#dg_btn').swapClass('btn_Dora_bs', 'btn_Dora_bstop').html('<b>纭璁や唬璐</b>').attr('id', '');
            //Y.get('#hm_btn').swapClass('btn_Dora_bs', 'btn_Dora_bstop').html('<b>鍙戣捣鍚堜拱</b>').attr('id', '');
            Y.get('#dg_btn').swapClass('btn_Dora_bs', 'btn_Dora_bstop').html('<b>绯荤粺鍗囩骇涓</b>').attr('id', '');
            Y.get('#hm_btn').hide();
        }

        Class.C('lotid', parseInt(this.get('#lotid').val()));
        Y.lib.AdsPosition({
            adsurl: 'https://www.500.com/static/info/icon/tradewanfa/bjdc.xml',
            imgnode: '<span title="{$title}" style="position: absolute; display: inline-block; line-height: 1; left: {$imgleft}px; top: {$imgtop}px; z-index: 151;"><img src="{$imgurl}"></span>',
            nodeid: 'dt.clearfix div.dc a[title*=鍖椾含鍗曞満]',
            headspanid: 'div.b-top-info div.dc_w',
            lotid: 9,
            type: 0
        });
        //鍖楀崟杩囧叧鏂瑰紡鏄鐢眏s鎷兼帴鑰屾垚
        Y.onMsg('gginfo-change', function(data) {
            if (data) {
                Y.lib.AdsPosition({
                    adsurl: 'https://www.500.com/static/info/icon/tradewanfa/bjdc.xml',
                    imgnode: '<span style="position: relative; display: inline-block;"><span title="{$title}" style="position: absolute; display: inline-block; line-height: 1; left:{$imgleft}px; top:{$imgtop}px; z-index: 9999;"><a href="{$openurl}" target="_blank"><img src="{$imgurl}"></a></span></span>',
                    nodeid: 'dt.clearfix div.dc a',
                    headspanid: 'div.b-top-info div.dc_w',
                    lotid: 9,
                    type: 1
                });
            }
        });
        // 鍙戣捣浠ｈ喘
        Yobj.watchIsBuy('#dg_btn,#hm_btn');
        Y.get('#dg_btn').click(function() {
            if (Yobj.checkStopBuy(this)) { return; }
            Y.checkBuyState(function() {
                Y.postMsg('msg_do_dg');
            });
        });

        // 鍙戣捣鍚堜拱
        Y.get('#hm_btn').click(function() {
            if (Yobj.checkStopBuy(this)) { return; }
            Y.checkBuyState(function() {
                Y.postMsg('msg_do_hm');
            });
        });
        // 杩囨护
        Y.get('#filter_btn').click(function() {
            //Y.checkBuyState(function (){
            Y.postMsg('msg_do_filter');
            //});			
        });

        //鍒涘缓涓涓鍏鍏卞脊绐, 浣跨敤msg_show_dlg杩涜岃皟鐢
        this.infoLay = this.lib.MaskLay('#defLay', '#defConent');
        this.infoLay.addClose('#defCloseBtn', '#defTopClose a');
        this.get('#defLay div.tips_title').drag(this.get('#defLay'));
        this.infoLay.noMask = self != top;

        // 鎻愪緵寮圭獥鏈嶅姟
        this.onMsg('msg_show_dlg', function(msg, fn, forbid_close) {
            this.infoLay.pop(msg, fn, forbid_close);
            if (Y.C('autoHeight')) {
                this.infoLay.panel.nodes[0].style.top = Y.C('clientY') - 80 + 'px';
            }
        });

        this.goTop = this.one('a.back_top');
        this.rightArea = this.get('#right_area');
        this.mainArea = this.get('#main');
        if (this.ie && this.ie == 6) {
            this.goTop.style.position = 'absolute';
            this.goTop.style.left = '750px';
        } else {
            setTimeout(function() {
                Y.goTop.style.left = Y.rightArea.getXY().x + 'px';
            }, 500);
        }
        this.get(window).scroll(function() {
            clearTimeout(Class.C('scrollTimer'));
            if (Y.ie && Y.ie == 6) {
                Class.C('scrollTimer', setTimeout(Y.scrollStillIE6.proxy(Y), 100));
            } else {
                Class.C('scrollTimer', setTimeout(Y.scrollStill.proxy(Y), 100));
            }
        });

        //	log('椤甸潰杞藉叆鑰楁椂锛' + (new Date() - d))

        //璁剧疆琛ㄥご娴鍔
        if (Yobj.get('#vsTable').size() === 0) {
            return; //濂栭噾璁＄畻鍣ㄦ病鏈夎〃澶存诞鍔
        }
        this.get('<div id="#title_float"></div>').insert().setFixed({
            area: '#vsTable',
            offset: 0,
            init: function() {
                var This = this,
                    title = this.area.find('table').one(0),
                    floatTitle = title.cloneNode(true);
                this.get(floatTitle).insert(this);
                this.floatTitle = floatTitle;
                this.title = title;
                this.hide();
                Y.get(window).resize(function() {
                    This.setStyle('left:' + (This.area.getXY().x) + 'px;width:' + (This.area.prop('offsetWidth')) + 'px')
                });
            },
            onin: function() {
                this.show();
                this.title.swapNode(this.floatTitle);
                var offset = this.ns.ie == 6 ? 2 : 0;
                this.setStyle('left:' + (this.area.getXY().x + offset) + 'px;width:' + this.area.prop('offsetWidth') + 'px')
            },
            onout: function() {
                this.hide();
                this.title.swapNode(this.floatTitle);
            }
        });
    },

    scrollStill: function() {
        var window_size = Y.getSize();
        Y.goTop = Y.get('a.back_top');
        Y.mainArea = Y.get('#main');
        Y.leftArea = Y.get('#main div.dc_l');
        Y.rightArea = Y.get('#main div.dc_r');
        var right_xy = Y.rightArea.getXY();
        var right_size = Y.rightArea.getSize();
        if (window_size.scrollTop + window_size.offsetHeight > Y.mainArea.getXY().y + Y.mainArea.getSize().offsetHeight + 10) {
            Y.goTop.setStyle('position', 'absolute').setStyle('bottom', 0).setStyle('left', '780px');
        } else {
            Y.goTop.setStyle('position', 'fixed').setStyle('bottom', '10px').setStyle('left', right_xy.x + 'px');
        }
        if (window_size.scrollTop <= right_xy.y ||
            right_xy.y + right_size.offsetHeight + 90 > window_size.scrollTop + window_size.offsetHeight ||
            Y.leftArea.getSize().offsetHeight - 90 < right_size.offsetHeight) {
            Y.goTop.hide();
        } else {
            Y.goTop.show();
        }
    },

    scrollStillIE6: function() {
        var window_size = Y.getSize();
        Y.goTop = Y.get('a.back_top');
        Y.mainArea = Y.get('#main');
        Y.leftArea = Y.get('#main div.dc_l');
        Y.rightArea = Y.get('#main div.dc_r');
        var right_xy = Y.rightArea.getXY();
        var right_size = Y.rightArea.getSize();
        if (window_size.scrollTop + window_size.offsetHeight > Y.mainArea.getXY().y + Y.mainArea.getSize().offsetHeight + 10) {
            Y.goTop.setStyle('top', '').setStyle('bottom', 0);
        } else {
            Y.goTop.setStyle('top', window_size.scrollTop + window_size.offsetHeight - 310 + 'px');
        }
        if (window_size.scrollTop <= right_xy.y ||
            right_xy.y + right_size.offsetHeight + 90 > window_size.scrollTop + window_size.offsetHeight ||
            Y.leftArea.getSize().offsetHeight - 90 < right_size.offsetHeight) {
            Y.goTop.hide();
        } else {
            Y.goTop.show();
        }
    },
    checkBuyState: function(fn) {
        var that = this;
        this.postMsg('msg_login', function() {
            fn.call(that);
        });
    },
    showStopInfo: function() {
        this.popStopDlg();
        this.hideHmlTitle();
    },
    hideHmlTitle: function() {
        var isLogin = this.one('#top_user_info').style.display != 'none';
        if (!isLogin) {
            this.get('#gotohmlurl').hide();
        } else {
            this.get('#gotohmlurl').show();
            this.postMsg('msg_close_addmoneydlg', true);
        };
    },
    popStopDlg: function() {
        if (this.one('#stopsalediv1')) {
            if (!this.stopDlg) {
                this.stopDlg = this.lib.MaskLay('#stopsalediv1');
                this.stopDlg.addClose('#stopsalediv_c1');
                //this.get('#info_dlg div.tips_title').drag('#info_dlg');
            }
            this.stopDlg.pop();
        } else {
            this.alert('璇ュ僵绉嶅凡鍋滃敭锛');
        }
    }

});
//璁剧疆鏌愪釜鏍囩惧湪鏌愪釜鍖哄煙鍐呮槸闈欐㈢殑
Class.fn.setFixed = function(opt) {
    var Y = this.ns,
        Yn = this,
        ini = this.ns.mix({
            onin: Y.getNoop(), //绉诲叆
            onout: Y.getNoop(), //绉诲嚭鍖哄煙
            area: document.body, //榛樿ゅ尯鍩熶负body
            offset: 0 //鍋忕Щ
        }, opt),
        areaTop, clearCache, isout = true;
    this.area = this.get(ini.area);
    if (Y.ie == 6 && !Y.C('-html-bg-fixed')) { //淇姝ie6闂鐑
        Y.C('-html-bg-fixed', true);
        var ds = document.documentElement.style;
        ds.backgroundImage = 'url(about:blank)';
        ds.backgroundAttachment = 'fixed';
    }
    if (window.Node) { //娣诲姞IE鐙鏈夋柟娉 replaceNode, swapNode
        Node.prototype.replaceNode = function($target) {
            return this.parentNode.replaceChild($target, this);
        }
        Node.prototype.swapNode = function($target) {
            var $targetParent = $target.parentNode;
            var $targetNextSibling = $target.nextSibling;
            var $thisNode = this.parentNode.replaceChild($target, this);
            $targetNextSibling ? $targetParent.insertBefore($thisNode, $targetNextSibling) : $targetParent.appendChild($thisNode);
            return this;
        }
    }
    if (opt.init) {
        opt.init.call(this)
    }
    this.get(window).scroll(handle);

    function handle() {
        clearTimeout(clearCache);
        if (!areaTop) { //浼樺寲婊氬姩鏃舵瘡娆¤＄畻鍖哄煙浣嶇疆
            clearCache = setTimeout(function() {
                areaTop = false
            }, 50);
            areaTop = Y.get(ini.area).getXY().y;
        }
        var sTop = Math.max(document.body.scrollTop || document.documentElement.scrollTop);
        if (sTop > areaTop) { //璺熻釜瀵归綈
            if (isout) {
                isout = false;
                ini.onin.call(Yn, ini.area);
                Yn.each(function(el) { //瀛樺偍top鍊
                    Y.get(el).data('-fixed-before-top', el.style.top);
                })
            }
            if (Y.ie == 6) {
                Yn.each(function(el) {
                    el.style.position = 'absolute';
                    el.style.setExpression('top', 'eval((document.documentElement||document.body).scrollTop+' + ini.offset + ') + "px"')
                })
            } else {
                Yn.setStyle('position:fixed;top:' + ini.offset + 'px');
            }
        } else { //鍋滄㈡诞鍔ㄥ归綈
            if (!isout) {
                isout = true;
                ini.onout.call(Yn, ini.area);
            }
            if (Y.ie == 6) {
                Yn.each(function(el) {
                    el.style.removeExpression('top');
                    el.style.top = Y.get(el).data('-fixed-before-top') || '';
                })
            } else {
                Yn.each(function(el) {
                    el.style.position = '';
                    el.style.top = Y.get(el).data('-fixed-before-top') || '';
                })
            }
        }
    }
    return this
};
//鍙风爜绡
Class('CodeSkep', {
    ready: true,
    use: 'mask',
    index: function() {
        var mod = this;
        this.skepUrl = '/main/getapicode.php';
        try { this._addDlg(); } catch (e) { return }
        setTimeout(function() {
            Yobj.getTip && Yobj.getTip().panel.setStyle('zIndex', 999999);
        }, 1000);
        this._initTag();
        this.onMsg('msg_close_addmoneydlg', function(noReply) {
            var isNotMoney = true;
            this.noReply = !!noReply;
            mod.addSkep(true, isNotMoney);
        });
        this.get('a.add2Skep_s').click(function() {
            __this.postMsg('msg_click_listen', 'jyq');
            Y.postMsg('msg_login', function() {
                mod.addSkep(true)
            });
        });
        var __this = this,
            murl = Class.C('url-trade') + '/useraccount/default.php?url=',
            hmlUrl = murl + Class.C('url-space') + '/pages/userbasket/';
        this.get('#lookskep, #lookskep2, #lookskep3').attr('href', hmlUrl);
        this.get('#share2lt').click(function() {
            var url = Class.C('url-space') + '/pages/userbasket/index.php?act=ajax&mod=sharebbs&callback=share_end&id=' + __this.C('skepid');
            __this.postMsg('msg_click_listen', 'fxbbs');
            window['share_end'] = function(json) {
                var state, kankan = Yobj.getSubDomain('bbs') + '/forum.php?mod=viewthread&tid=' + json['tid'];
                switch (json.msg) {
                    case 1:
                        clearTimeout(__this.dlgSmallTimer);
                        __this.dlgSmall.pop('鍒嗕韩鎴愬姛锛岀珛鍒诲幓<a href="' + kankan + '" target="_blank" style="blue">鐪嬬湅</a>锛');
                        __this.get('#share2lt').hide();
                        __this.dlgSmallTimer = setTimeout(function() {
                            __this.dlgSmall.close();
                        }, 3000);
                        break;
                    case 2:
                        __this.dlgSmall.pop('鍒嗕韩鎴愬姛, 姝ｅ湪绛夊緟瀹℃牳');
                        __this.get('#share2lt').hide();
                        break;
                    case -7:
                        __this.alert('鎮ㄥソ, 鎮ㄥ凡缁忓垎浜杩囨ゆ柟妗堬紒');
                        break;
                    default:
                        __this.alert('鍒嗕韩澶辫触');
                }
            }
            __this.use(url);
        });
    },
    _addDlg: function() {
        this.dlgOk = this.lib.MaskLay('#lay_hmlend');
        this.dlgOk.addClose('#lay_hmlend_c');
        this.dlgSmall = this.lib.MaskLay('#dlg_small', '#dlg_small_c');
        this.dlgSmall.addClose('#dlg_small_k,#share2lt');
    },
    getTitle: function(str) {
        var lot = ({ 34: '璁╃悆鑳滃钩璐', 40: '鎬昏繘鐞冩暟', 41: '涓婁笅鍗曞弻', 42: '姣斿垎' })[Class.config('playId')],
            exp = this.get('#expect').val(),
            type = '澶嶅紡鏂规';
        return lot + '绗 ' + exp + ' 鏈' + type + ' - ' + str;
    },
    errTip: function(txt) {
        var tag = this.get('#tag_over');
        tag.html(txt).show(!!txt);
        Y.get('#tag_ok').hide();
    },
    _initTag: function() {
        var mod = this;
        this.userTags = [];
        var text = this.get('#lay_2Skep_tagInput'),
            t,
            tt = text.one();
        text.focus(function() { //鏍囩捐緭鍏ユ
            if (this.value.trim() == this.defaultValue) {
                this.value = '';
            }
            var This = this;
            t = setInterval(function() {
                var s = This.value.trim().replace(/\s+/g, ' '),
                    a = only(s.split(' '), 10)
                if (This.value.trim().length == 0) {
                    mod.errTip('鏍囩句笉鑳戒负绌');
                } else if (a.length > 3) {
                    mod.errTip('鏍囩句釜鏁拌秴杩3涓');
                } else if (/\S{10,}/.test(This.value.trim())) {
                    mod.errTip('鏍囩鹃暱搴﹁秴杩囦釜10涓瀛楃');
                } else {
                    mod.errTip();
                }
                mod.userTags = a //.slice(0, 3);
            }, 100);
        }).blur(function() {
            clearInterval(t);
            if (this.value.trim() == '') {
                mod.userTags = [];
                return this.value = this.defaultValue;
            }
            this.value = mod.userTags.join(' ');
            mod.get('#tag_over').hide();
        });
        this.get('#lay_2Skep_tags').live('a', 'click', function(e) { //娣诲姞绯荤粺鏍囩
            mod.userTags.push(this.innerHTML);
            mod.userTags = only(mod.userTags, 10);
            mod.errTip(mod.userTags.length > 3 ? '鏍囩句釜鏁拌秴杩3涓' : false);
            tt.value = mod.userTags.join(' ');
            e.end();
            e.stop();
            return false;
        });
        this.get('#lay_2Skep_chtag').click(function() { //鏇存崲鍙閫夋爣绛
            mod._rndTag();
        });
        this.get('#btn_saveTag').click(function() {
            if (mod.userTags.length > 3) {
                return text.doProp('select');
            } else {
                var err = mod.userTags.filter(function(a) {
                    return a.length > 10
                });
                if (err.length) {
                    return text.doProp('select');
                }
            }
            mod.sendTag();
        });

        function only(arr, len) { //鍞涓鍖栨爣绛
            var o = {},
                b = [];
            arr.each(function(k) {
                if (!o[k]) {
                    o[k] = 1;
                    //k=k.slice(0, len);
                    b.push(k)
                }
            });
            return b;
        }
    },
    _saveList: [], //鍒氭敹钘忕殑鍙风爜
    _sendAdd: function(isNotMoney) { //鏀惰棌鍙风爜
        var d = this.currentData;
        if (isNotMoney && this._saveList.indexOf(this.get('#playid').val() + '~' + d.codes) > -1) {
            return; //this.alert('鎮ㄥソ, 浣犲垰鍒氬凡缁忔敹钘忚繃杩欑粍鍙风爜!');
        }
        var data = {
            type: 2,
            lotid: this.get('#lotid').val(),
            playid: this.get('#playid').val(),
            expect: this.get('#expect').val(),
            code: d.codes,
            complete: 1,
            //tag:encodeURIComponent(this.userTags.join('|')),
            allmoney: d.zhushu * 2,
            remark: ''
        };
        !this.noReply && this.alert('姝ｅ湪灏嗗彿鐮佷繚瀛樺埌鎮ㄧ殑鍙风爜绡...', false, true);
        this.ajax({
            url: this.skepUrl,
            type: 'POST',
            data: data,
            end: function(data, i) {
                var info, err = '鏀惰棌鍙风爜澶辫触, 璇烽噸璇!';
                this.alert.close();
                if (!data.error) {
                    if (info = this.dejson(data.text)) {
                        switch (info.code) {
                            case 1:
                                this._saveList.push(this.get('#playid').val() + '~' + d.codes);
                                this.dlgSmall.noMask = true;
                                this.get('#share2lt').show();
                                this.C('skepid', info.str);
                                if (isNotMoney) {
                                    !this.noReply && this.dlgSmall.pop('宸叉垚鍔熷姞鍏ュ彿鐮佺, 鎮ㄥ彲浠ョ◢鍊欒喘涔');
                                } else {
                                    this.dlgOk.pop()
                                }
                                var This = this,
                                    t;
                                this.postMsg('msg.hml.save.success');
                                return this.dlgSmallTimer = setTimeout(function() {
                                    This.dlgSmall.close();
                                }, 4000);
                                break;
                            case 2:
                                var murl = Class.C('url-trade') + '/useraccount/default.php?url=',
                                    hmlUrl = murl + Class.C('url-space') + '/pages/userbasket/';
                                err = '鎮ㄥソ锛屽彿鐮佺浠婃棩瀹归噺宸叉弧锛岃锋竻绌<a href="' + hmlUrl + '" target="_blank" style="blue" onclick="Yobj.alert.close()">鍙风爜绡</a>鍚庡啀鏀惰棌';
                        }
                    }
                }
                if (!this.noReply) {
                    this.alert(err);
                }
            }
        });
    },
    _rndTag: function() { //鏇存崲鏍囩
        if (this.C('query_tag')) {
            return;
        }
        this.get('#lay_2Skep_chtag').addClass('ico_loading');
        this.C('query_tag', true);
        this.ajax({
            url: this.skepUrl + '?type=3&num=3&lotid=' + this.get('#lotid').val(),
            end: function(data, i) {
                var info, tags;
                this.get('#lay_2Skep_chtag').removeClass('ico_loading');
                this.C('query_tag', false);
                if (!data.error) {
                    if (info = this.dejson(data.text)) {
                        tags = info.str;
                        if (tags instanceof Array) {
                            this.get('#lay_2Skep_tags a').empty(true); //鍒犻櫎鍘熸湁
                            this.isInitTags = true;
                            tags.each(function(tag) {
                                this.get('<a class="tag" href="javascript:;">' + tag + '</a>').insert('#lay_2Skep_tags');
                            }, this)
                        }
                    }
                }
            }
        });
    },
    sendTag: function() {
        if (this.C('sendTag')) { return; }
        if (this.userTags.length == 0) {
            this.errTip('鏍囩句笉鑳戒负绌');
            return this.one('#lay_2Skep_tagInput').select();
        }
        this.C('sendTag', true);
        this.get('#ico_tagadd').addClass('ico_loading');
        this.get('#tag_ok').hide();
        clearTimeout(this.tagOkTimer);
        this.ajax({
            url: this.skepUrl + '?type=4&cid=' + this.C('skepid') + '&lotid=' + this.get('#lotid').val(),
            type: 'POST',
            data: {
                type: 4,
                cid: this.C('skepid'),
                tag: encodeURIComponent(this.userTags.join('|'))
            },
            end: function(data, i) {
                var info, tags;
                this.get('#ico_tagadd').removeClass('ico_loading');
                this.C('sendTag', false);
                if (!data.error) {
                    if (info = this.dejson(data.text)) {
                        if (info.code == 1) {
                            this.get('#tag_ok').show();
                            this.tagOkTimer = setTimeout(function() {
                                Y.get('#tag_ok').hide();
                            }, 2000);
                            return this.clearTag();
                        }
                    }
                }
                this.alert('娣诲姞鏍囩惧け璐ワ紝璇烽噸璇!');
            }
        });
    },
    clearTag: function() {
        var t = this.one('#lay_2Skep_tagInput');
        this.get('#tag_over').hide();
        this.userTags = [];
        t.value = t.defaultValue;
        t.blur();
    },
    codeTpl: '',
    isInitTags: false,
    getSubType: function() { return '' },
    addSkep: function(isListCode, isNotMoney) {
        var msg, data, gg_info, code_info, tz_info;
        code_info = this.postMsg('msg_get_codes_4_submit').data; //{codes, danma}
        gg_info = this.postMsg('msg_get_gg_info_more').data;
        1 //{"gggroup":3, "sgtypename":"3涓1,5涓1","sgtype":"3,14"}
        tz_info = this.postMsg('msg_get_touzhu_result_4_submit').data; //{"zhushu":0,"beishu":0,"totalmoney":0}
        if (msg = this.checkCode(gg_info, tz_info, code_info)) {
            return this.alert(msg);
        }
        var html = this.data2Html(gg_info, tz_info, code_info);
        this.get('#lay_2Skep_list').html(html.join(''));
        if (!this.isInitTags) {
            this._rndTag();
        }
        this.currentData = this.formatSaveCode(gg_info, tz_info, code_info);
        this.clearTag();
        this._sendAdd(isNotMoney);
    },
    checkCode: function(gg, tz, code) {
        if (code.codes == '') {
            return '鎮ㄥソ, 璇烽夋嫨濂芥偍瑕佹姇娉ㄧ殑姣旇禌銆'
        } else if (gg.sgtype == '') {
            return '鎮ㄥソ, 璇烽夋嫨濂芥偍瑕佹姇娉ㄧ殑杩囧叧鏂瑰紡銆'
        }
    },
    data2Html: function(gg, tz, code) {
        if (code.danma != '') {
            return ['銆愯儐銆' + code.danma + '<br/>銆愭嫋銆' + code.t + '<br/>杩囧叧鏂瑰紡: ' + gg.sgtypename];
        } else {
            return [code.codes + '<br/>杩囧叧鏂瑰紡: ' + gg.sgtypename];
        }
    },
    formatSaveCode: function(gg, tz, code) {
        return {
            codes: '{"codes":"' + this.ch2num(code.codes) + '","danma":"' + this.ch2num(code.danma) + '","sgtype":"' + gg.sgtype + '"}',
            zhushu: tz.zhushu
        };
    },
    repMap: [{
        '10': '1:0',
        '20': '2:0',
        '21': '2:1',
        '30': '3:0',
        '31': '3:1',
        '32': '3:2',
        '40': '4:0',
        '41': '4:1',
        '42': '4:2',
        '50': '5:0',
        '51': '5:1',
        '52': '5:2',
        '3A': '鑳滃叾[浠栧畠]',
        '00': '0:0',
        '11': '1:1',
        '22': '2:2',
        '33': '3:3',
        '44': '4:4',
        '1A': '骞冲叾[浠栧畠]',
        '01': '0:1',
        '02': '0:2',
        '12': '1:2',
        '03': '0:3',
        '13': '1:3',
        '23': '2:3',
        '04': '0:4',
        '14': '1:4',
        '24': '2:4',
        '05': '0:5',
        '15': '1:5',
        '25': '2:5',
        '0A': '璐熷叾[浠栧畠]'
    }, {
        '3': '鑳',
        '1': '骞',
        '0': '璐'
    }, {
        '0': '涓奬\+鍗',
        '1': '涓奬\+鍙',
        '2': '涓媆\+鍗',
        '3': '涓媆\+鍙',
        '7': '7\\+'
    }],
    ch2num: function(ch) {
        this.repMap.each(function(reg) {
            for (var k in reg) {
                ch = ch.replace(RegExp(reg[k], 'g'), k)
            }
        });
        ch = ch.replace(/-/g, '');
        if (this.C('playName') != 'bf' && this.C('playName') != 'bq') {
            // ch = ch.replace(/,/g,'');
        }
        return ch;
    }
});

//鐐瑰嚮缁熻
Class({
    ready: true,
    index: function() {
        this.onMsg('msg_click_listen', function(type) {
            var id = 'bjdc_' + type,
                lid = this.getId(id);
            if (lid) {
                this.dcsMultiTrack(lid)
            }
        });
    },
    dcsMultiTrack: function(id) {
        if (typeof(dcsMultiTrack) == 'function') {
            dcsMultiTrack(
                'DCSext.button_t',
                id.slice(0, 2) + '000000',
                'DCSext.button_w',
                id.slice(0, 4) + '0000',
                'DCSext.button_b',
                id.slice(0, 6) + '00',
                'DCSext.button_c',
                id,
                'DCSext.button_n',
                'ssyg_gm'
            );
        }
    },
    getId: (function() {
        var listenId = {
            "sfc_fxbbs": "10910101",
            "rj_fxbbs": "10910102",
            "bjdc_fxbbs": "10910103",
            "jczq_fxbbs": "10910104",
            "ssq_fxbbs": "10910105",
            "dlt_fxbbs": "10910106",
            "sd_fxbbs": "10910107",
            "pls_fxbbs": "10910108",
            "sfc_jyq": "10910109",
            "rj_jyq": "10910110",
            "bjdc_jyq": "10910111",
            "jczq_jyq": "10910112",
            "ssq_jyq": "10910113",
            "dlt_jyq": "10910114",
            "sd_jyq": "10910115",
            "pls_jyq": "10910116",
            "sfc_faxq": "10910117",
            "rj_faxq": "10910118",
            "bjdc_faxq": "10910119",
            "jczq_faxq": "10910120",
            "ssq_faxq": "10910121",
            "dlt_faxq": "10910122",
            "sd_faxq": "10910123",
            "pls_faxq": "10910124",
            "sfc_drhm": "10910125",
            "rj_drhm": "10910126",
            "bjdc_drhm": "10910127",
            "jczq_drhm": "10910128",
            "ssq_drhm": "10910129",
            "dlt_drhm": "10910130",
            "sd_drhm": "10910131",
            "pls_drhm": "10910132",
            "hml_wzdb": "10910133"
        };
        return function(key) {
            return listenId[key];
        }
    })()
});