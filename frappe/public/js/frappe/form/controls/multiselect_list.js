frappe.ui.form.ControlMultiSelectList = frappe.ui.form.ControlData.extend({
	make_input() {
		let template  = `
			<div class="multiselect-list dropdown">
				<div class="form-control cursor-pointer dropdown-toggle input-sm" data-toggle="dropdown">
					<span class="status-text ellipsis"></span>
				</div>
				<ul class="dropdown-menu">
					<li class="dropdown-input-wrapper">
						<input type="text" class="form-control input-sm">
					</li>
					<div class="selectable-items">
					</div>
				</ul>
			</div>
		`;

		this.$list_wrapper = $(template);
		this.$input = $('<input>');
		this.$list_wrapper.prependTo(this.input_area);
		this.$list_wrapper.on('click', '.dropdown-menu', e => {
			e.stopPropagation();
		});
		this.$list_wrapper.on('click', '.selectable-item', e => {
			let $target = $(e.currentTarget);
			this.toggle_select_item($target);
		});
		this.$list_wrapper.on('input', 'input', e => {
			let txt = e.target.value;
			let filtered_options = this._options.filter(opt => {
				let match = false;
				if (this.values.includes(opt.value)) {
					return true;
				}
				match = Awesomplete.FILTER_CONTAINS(opt.label, txt);
				if (!match) {
					match = Awesomplete.FILTER_CONTAINS(opt.value, txt);
				}
				return match;
			});
			this.set_selectable_items(filtered_options);
		});
		this.$list_wrapper.on('keydown', 'input', e => {
			if (e.key === 'ArrowDown') {
				this.highlight_item(1);
			} else if (e.key === 'ArrowUp') {
				this.highlight_item(-1);
			} else if (e.key === 'Enter') {
				if (this._$last_highlighted) {
					this.toggle_select_item(this._$last_highlighted);
					return false;
				}
			}
		});

		this.$list_wrapper.on('show.bs.dropdown', () => {
			this.set_options()
				.then(() => {
					this.set_selectable_items(this._options);
				});
		});

		this.set_input_attributes();
		this.values = [];
		this.highlighted = -1;
	},

	set_input_attributes() {
		this.$list_wrapper
			.attr("data-fieldtype", this.df.fieldtype)
			.attr("data-fieldname", this.df.fieldname);

		this.set_status(this.get_placeholder_text());

		if (this.doctype) {
			this.$list_wrapper.attr("data-doctype", this.doctype);
		}
		if(this.df.input_css) {
			this.$list_wrapper.css(this.df.input_css);
		}
		if(this.df.input_class) {
			this.$list_wrapper.addClass(this.df.input_class);
		}
	},

	toggle_select_item($selectable_item) {
		$selectable_item.toggleClass('selected');
		let value = decodeURIComponent($selectable_item.data().value);

		if ($selectable_item.hasClass('selected')) {
			this.values.push(value);
		} else {
			this.values = this.values.filter(val => val !== value);
		}
		this.parse_validate_and_set_in_model('');
		this.update_status();
	},

	update_status() {
		let text;
		if (this.values.length === 0) {
			text = this.get_placeholder_text();
		} else if (this.values.length === 1) {
			let val = this.values[0];
			text = this._options.find(opt => opt.value === val).label;
		} else {
			text = __('{0} values selected', [this.values.length]);
		}
		this.set_status(text);
	},

	get_placeholder_text() {
		return `<span class="text-extra-muted">${this.df.placeholder || ''}</span>`;
	},

	set_status(text) {
		this.$list_wrapper.find('.status-text').html(text);
	},

	set_options() {
		let promise = Promise.resolve();

		function process_options(options) {
			return options.map(option => {
				if (typeof option === 'string') {
					return {
						label: option,
						value: option
					};
				}
				if (!option.label) {
					option.label = option.value;
				}
				return option;
			});
		}

		if (this.df.get_data) {
			let value = this.df.get_data();
			if (!value) {
				this._options = [];
			} else if (value.then) {
				promise = value.then(options => {
					this._options = process_options(options);
				});
			} else {
				this._options = process_options(value);
			}
		} else {
			this._options = process_options(this.df.options);
		}
		return promise;
	},

	set_selectable_items(options) {
		let html = options.map(option => {
			let encoded_value = encodeURIComponent(option.value);
			let selected = this.values.includes(option.value) ? 'selected' : '';
			return `<li class="selectable-item ${selected}" data-value="${encoded_value}">
				${option.label}
				<span class="octicon octicon-check text-muted"></span>
			</li>`;
		}).join('');
		if (!html) {
			html = `<li class="text-muted">${__('No values to show')}</li>`;
		}
		this.$list_wrapper
			.find('.selectable-items')
			.html(html);

		this.highlighted = -1;
	},

	get_value() {
		return this.values;
	},

	highlight_item(value) {
		this.highlighted += value;

		if (this.highlighted < 0) {
			this.highlighted = 0;
		}
		let $items = this.$list_wrapper.find('.selectable-item');
		if (this.highlighted > $items.length - 1) {
			this.highlighted = $items.length - 1;
		}

		let $item = $items[this.highlighted];

		if (this._$last_highlighted) {
			this._$last_highlighted.removeClass('highlighted');
		}
		this._$last_highlighted = $($item).addClass('highlighted');
		this.scroll_dropdown_if_needed($item);
	},

	scroll_dropdown_if_needed($item) {
		if ($item.scrollIntoView) {
			$item.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'start' });
		} else {
			$item.parentNode.scrollTop = $item.offsetTop - $item.parentNode.offsetTop;
		}
	}
});
