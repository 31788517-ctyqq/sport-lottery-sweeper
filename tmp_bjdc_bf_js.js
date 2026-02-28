/* TableSelector_BF 鍖楀崟瀵归樀鍒楄〃閫夋嫨鍣(姣斿垎鐜╂硶)
------------------------------------------------------------------------------*/
Class( 'TableSelector > TableSelector_BF', {

	initVsTrs : function(vs_lines) {
		var Y = this;
		this.vsTrs = Y.need(vs_lines).each( function(tr, i) {
			var vs_info = Y.dejson(tr.getAttribute('value'));
			var tr2 = document.getElementById('sp_lines_' + vs_info.index);
			var cks = tr2.getElementsByTagName('input');
			this[i] = Y.lib.LineSelector_BF( {
				tr        : tr,
				vsIndex   : tr.getElementsByTagName('input')[0],
				expandSp  : Y.need('a.expand_sp', tr).one(),
				vsInfo    : vs_info,
				tr2       : tr2,
				spTag     : Y.get('span.sp_value', tr2),
				vsOptions : tr2.getElementsByTagName('label'),
				vsCheckAllWin  : cks[10],
				vsCheckAllDraw : cks[16],
				vsCheckAllLose : cks[27]
			} );
			Y.vsInfo[vs_info.index] = vs_info;  //瀛樺偍鎵鏈夋瘮璧涚殑鐩稿叧鏁版嵁
		}, [] );
	},

	// 杩斿洖淇鏀规椂閲嶇幇涔嬪墠閫夋嫨鐨勬瘮璧
	restoreCodes : function(codes) {
		codes.each( function(obj) {
			this.vsTrs[obj.index - 1].checkCertainVsOptions(obj.arr);
		}, this );
	},

	// 鏇存柊SP鍊
	updateSP : function() {
		this.ajax( {
		url :	'https://www.500.com/static/public/bjdc/xml/sp/just_' + Class.config('expect') + '_' + Class.config('playId') + '.xml',
		end :	function(data) {
					var Y = this;
					if (data.xml) {
						this.qXml('/w/*', data.xml, function(obj, i) {
							var sp_values = new Array();
							for (var j = 1, l = Class.config('codeValue').length; j <= l; j++) {
								sp_values.push(obj.items['c' + j]);
							}
							this.vsTrs[i].updateSP(sp_values);
						} );
						setTimeout( function() { Y.updateSP() }, 5*60*1000 );
					} else {
						setTimeout( function() { Y.updateSP() }, 5000 );  //澶辫触鍚庣煭鏃堕棿鍐呭啀娆¤锋眰
					}
				}
		} );
	}

} );


/* LineSelector_BF 鍖楀崟琛岄夋嫨鍣(姣斿垎鐜╂硶)
------------------------------------------------------------------------------*/
Class( 'LineSelector_BF', {

	index : function(config) {

		this.vsLine     = config.tr;
		this.vsIndex    = config.vsIndex;
		this.spLine     = config.tr2;
		this.expandSp   = config.expandSp;
		this.spTag      = config.spTag;
		this.vsOptions  = { 'win':[], 'draw':[], 'lose':[] }
		for (i = 0, l = config.vsOptions.length; i< l; i++) {
			if (i < 10) {
				this.vsOptions.win.push(config.vsOptions[i]);
			} else if (i < 15) {
				this.vsOptions.draw.push(config.vsOptions[i]);
			} else {
				this.vsOptions.lose.push(config.vsOptions[i]);
			}
		}
		this.vsCheckAll   = {
			'win'  : config.vsCheckAllWin,
			'draw' : config.vsCheckAllDraw,
			'lose' : config.vsCheckAllLose
		}
		this.vsInfo = config.vsInfo;

		this.disabled = this.vsInfo.disabled === 'yes';
		this.index = this.vsInfo.index;
		this.data       = [];  //鏈琛岀殑鎶曟敞缁撴灉
		this.data[24]   = undefined;
		this.codeValIdx = Class.config('codeValueIndex');

		this.bindEvent();
		if (this.disabled && !Class.config('stopSale')) {
			this.vsIndex.disabled = true;
		}
		this.vsIndex.checked = true;
		!this.disabled && this.initClearAll();  //鍒濆嬪叏涓嶉変腑

		// 鎺ユ敹娑堟伅锛屽彇娑堟煇涓閫夐」鐨勯夋嫨
		this.onMsg('msg_touzhu_cancel', function(line_index, ck_value) {
			if (this.index == line_index) {
				var ck_index, flag, ck;
				ck_index = this.getIndex(Class.config('codeValue'), ck_value);
				if (ck_index >= 15) {
					ck_index -= 15;
					flag = 'lose';
				} else if (ck_index >= 10) {
					ck_index -= 10;
					flag = 'draw';
				} else {
					flag = 'win';
				}
				ck = this.vsOptions[flag][ck_index].getElementsByTagName('input')[0];
				this.unCheck(ck);
				return false; //鍋滄㈡秷鎭浼犻
			}
		});

	},

	// 缁戝畾鐩稿叧浜嬩欢
	bindEvent : function() {
		var Y = this;

		// 榧犳爣缁忚繃姣忎竴琛屾椂鏀瑰彉鏍峰紡
		this.get(this.vsLine).hover( function() {
			this.style.backgroundColor = '#FEFFD1';
		}, function() {
			this.style.backgroundColor = '';
		} );

		// 灞曞紑闅愯棌SP鍊
		this.expandSp.onclick = function() {
			if (Y.spLine.style.display == 'none') {
				Y.expandSpArea();
			} else {
				Y.shrinkSpArea();
			}
			Y.C('autoHeight') && Y.postMsg('msg_update_iframe_height');
		}

		// 鐐瑰嚮闅愯棌鏌愬満姣旇禌
		this.vsIndex.onclick = function() {
			Y.hideLine();
		}

		if (this.disabled) return;

		// 鐐瑰嚮閫夐」杩涜屾姇娉
		for (var item in this.vsOptions) {
			this.vsOptions[item].each( function(the_label) {
				the_label.parentNode.onmousedown = function() {
					var ck = this.getElementsByTagName('input')[0];
					ck.checked ? Y.unCheck(ck) : Y.check(ck);
				}
			} );
		}

		// 鍏ㄩ/鍏ㄤ笉閫
		for (var item in this.vsCheckAll) {
			(function(item) {
				Y.vsCheckAll[item].parentNode.onmousedown = function() {
					var ck = this.getElementsByTagName('input')[0];
					ck.checked = !ck.checked;
					ck.checked ? Y.checkAll(item) : Y.clearAll(item);
				}
			})(item)
		}
	},

	check : function(ck) {
		this.data[this.codeValIdx[ck.value]] = ck.value;
		ck.checked = true;
		ck.parentNode.parentNode.style.backgroundColor = '#FFDAA4';
		this.allCheckedOrNot();
		this.changed();
	},

	unCheck : function(ck) {
		this.data[this.codeValIdx[ck.value]] = undefined;
		ck.checked = false;
		ck.parentNode.parentNode.style.backgroundColor = '';
		this.allCheckedOrNot();
		this.changed();
	},

	checkAll : function(i) {
		var code_value = Class.config('codeValue');
		switch (i) {
			case 'win'  : this.data.splice(0, 10, '鑳滃叾浠', '1:0', '2:0', '2:1', '3:0', '3:1', '3:2', '4:0', '4:1', '4:2'); break;
			case 'draw' : this.data.splice(10, 5, '骞冲叾浠', '0:0', '1:1', '2:2', '3:3'); break;
			case 'lose' : this.data.splice(15, 10, '璐熷叾浠', '0:1', '0:2', '1:2', '0:3', '1:3', '2:3', '0:4', '1:4', '2:4');
		}
		this.vsCheckAll[i].checked = true;
		this.vsOptions[i].each( function(the_label, _i) {
			the_label.getElementsByTagName('input')[0].checked = true;
			the_label.parentNode.style.backgroundColor = '#FFDAA4';
		}, this );
		this.changed();
	},

	clearAll : function() {
		if (arguments[0]) {
			var i = arguments[0];
			switch (i) {
				case 'win'  : this.data.splice(0, 10, undefined, undefined, undefined, undefined, undefined, undefined, undefined, undefined, undefined, undefined); break;
				case 'draw' : this.data.splice(10, 5, undefined, undefined, undefined, undefined, undefined); break;
				case 'lose' : this.data.splice(15, 10, undefined, undefined, undefined, undefined, undefined, undefined, undefined, undefined, undefined, undefined);
			}
			this.vsCheckAll[i].checked = false;
			this.vsOptions[i].each( function(the_label) {
				the_label.getElementsByTagName('input')[0].checked = false;
				the_label.parentNode.style.backgroundColor = '';
			}, this );
		} else {
			this.data = [];
			this.data[24] = undefined;
			for (var item in this.vsCheckAll) {
				this.vsCheckAll[item].checked = false;
				this.vsOptions[item].each( function(the_label) {
					the_label.getElementsByTagName('input')[0].checked = false;
					the_label.parentNode.style.backgroundColor = '';
				}, this );
			}
		}
		this.changed();
	},

	initClearAll : function() {
		var ck = this.spLine.getElementsByTagName('input');
		for (var i = 0, l = ck.length; i < l; i++) {
			ck[i].checked = false;
		}
	},

	hideLine : function() {  //闅愯棌褰撳墠琛
		if (this.vsLine.style.display != 'none') {
			this.getData().length > 0 && this.clearAll();
			this.spLine.style.display = 'none';
			this.vsLine.style.display = 'none';
			this.shrinkSpArea();
			!this.vsIndex.disabled && this.postMsg('msg_one_match_hided');
			Y.C('autoHeight') && Y.postMsg('msg_update_iframe_height');
		}
	},

	showLine : function() {  //鏄剧ず褰撳墠琛
		if (this.vsLine.style.display == 'none') {
			this.vsLine.style.display = '';
			this.vsIndex.checked = true;
			!this.vsIndex.disabled && this.postMsg('msg_one_match_showed');
			Y.C('autoHeight') && Y.postMsg('msg_update_iframe_height');
		}
	},

	expandSpArea : function() {
		this.spLine.style.display = '';
		this.expandSp.className = 'bf_btn expand_sp public_Dora';
		this.expandSp.innerHTML = '<b>闅愯棌SP鍊<s class="c_up"></s></b>';
	},

	shrinkSpArea : function() {
		this.spLine.style.display = 'none';
		this.expandSp.className = 'bf_btn expand_sp public_Lblue';
		this.expandSp.innerHTML = '<b>灞曞紑SP鍊<s class="c_down"></s></b>';
	},

	// 鑾峰彇鏈琛屾姇娉ㄦ暟鎹
	getData : function() {
		if (this.disabled) return [];
		return this.data.each( function(d) {
			d && this.push(d);
		}, [] );
	},

	// 妫娴嬪綋鍓嶅叏閫夋嗙殑鐘舵
	allCheckedOrNot : function() {
		var len = { 'win':0, 'draw':0, 'lose':0 };
		for (var item in this.vsOptions) {
			this.vsOptions[item].each( function (the_label) {
				var ck = the_label.getElementsByTagName('input')[0];
				ck.checked && len[item]++;
			}, this );
		}
		this.vsCheckAll.win.checked  = (len.win === 10);
		this.vsCheckAll.draw.checked = (len.draw === 5);
		this.vsCheckAll.lose.checked = (len.lose === 10);
	},

	// 閫変腑鏌愪簺鐗瑰畾鐨勯夐」
	checkCertainVsOptions : function(ck_value) {
		var code_value = Class.config('codeValue');
		ck_value.split(',').each( function(v) {
			var i, flag;
			i = this.getIndex(code_value, v);
			flag = 'win';
			if (i >= 15) {
				i -= 15;
				flag = 'lose';
			} else if (i >= 10) {
				i -= 10;
				flag = 'draw';
			}
			this.check(this.vsOptions[flag][i].getElementsByTagName('input')[0]);
		}, this );
		this.expandSpArea();
	},

	// 鏇存柊SP鍊
	updateSP : function(sp_values) {
		if (this.spTag && !this.disabled) {
			this.spTag.each( function(item, index) {
				var sp_old, sp_new;
				sp_old = parseFloat(item.innerHTML);
				sp_new = parseFloat(sp_values[index]);
				this.get(item).removeClass('red').removeClass('green');
				if (sp_new > sp_old) {
					this.get(item).addClass('red');
				} else if (sp_new < sp_old) {
					this.get(item).addClass('green');
				}
				item.innerHTML = sp_new ? sp_new.toFixed(2) : '--';
			}, this );
		}
	},

	changed : function() {
		this.postMsg('msg_line_selector_changed');
	}

} );
