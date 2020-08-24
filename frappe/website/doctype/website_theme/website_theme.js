// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

frappe.ui.form.on('Website Theme', {
	refresh(frm) {
		frm.set_intro(__('Default theme is set in {0}', ['<a href="#Form/Website Settings">'
			+ __('Website Settings') + '</a>']));

		frm.toggle_display(["module", "custom"], !frappe.boot.developer_mode);

		frm.add_custom_button(__('Configure Theme'), () => {
			const d = new frappe.ui.Dialog({
				title: __('Configure Theme'),
				fields: [
					{
						label: __('Font Styles'),
						fieldtype: 'Section Break'
					},
					{
						label: __('Google Font'),
						fieldtype: 'Data',
						fieldname: 'google_font',
						description: __('Add the name of a "Google Web Font" e.g. "Open Sans"')
					},
					{
						label: __('Font Size (px)'),
						fieldtype: 'Int',
						fieldname: 'font_size',
						default: 16
					},
					{
						label: __('Theme Colors'),
						fieldtype: 'Section Break',
					},
					{
						label: __('Primary Color'),
						fieldtype: 'Color',
						fieldname: 'primary_color'
					},
					{
						label: __('Dark Color'),
						fieldtype: 'Color',
						fieldname: 'dark_color'
					},
					{
						label: __('Text Color'),
						fieldtype: 'Color',
						fieldname: 'text_color'
					},
					{
						label: __('Background Color'),
						fieldtype: 'Color',
						fieldname: 'background_color'
					},
					{
						label: __('Misc'),
						fieldtype: 'Section Break',
					},
					{
						label: __('Navbar Style'),
						fieldtype: 'Select',
						fieldname: 'navbar_style',
						options: [
							'Light',
							'Dark'
						],
						default: 'Light'
					},
					{
						label: __('Enable Shadows'),
						fieldtype: 'Check',
						fieldname: 'enable_shadows'
					},
					{
						label: __('Enable Gradients'),
						fieldtype: 'Check',
						fieldname: 'enable_gradients'
					},
					{
						label: __('Rounded Corners'),
						fieldtype: 'Check',
						fieldname: 'enable_rounded',
						default: 1
					},
				],
				primary_action: (values) => {
					const {
						google_font,
						font_size,
						primary_color,
						dark_color,
						text_color,
						background_color,
						navbar_style,
						enable_shadows,
						enable_gradients,
						enable_rounded
					} = values;
					let scss_lines = [];
					let js_lines = [];
					if (google_font) {
						const google_font_slug = google_font.split(' ').join('+');
						const font_family_default = `'-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif'`;
						scss_lines.push(
							`@import url('https://fonts.googleapis.com/css?family=${google_font_slug}:400,300,400italic,700&subset=latin,latin-ext');`,
							`$font-family-sans-serif: "${google_font}", ${font_family_default};`
						);
					}
					if (primary_color) {
						scss_lines.push(
							`$primary: ${primary_color};`
						);
					}
					if (dark_color) {
						scss_lines.push(
							`$dark: ${dark_color};`
						);
					}
					if (text_color) {
						scss_lines.push(
							`$body-color: ${text_color};`
						);
					}
					if (background_color) {
						scss_lines.push(
							`$body-bg: ${background_color};`
						);
					}

					scss_lines.push(
						`$enable-shadows: ${Boolean(enable_shadows)};`
					);

					scss_lines.push(
						`$enable-gradients: ${Boolean(enable_gradients)};`
					);

					scss_lines.push(
						`$enable-rounded: ${Boolean(enable_rounded)};`
					);

					if (font_size) {
						scss_lines.push(
							'\n',
							`body {\n\tfont-size: ${font_size}px;\n}`
						);
					}

					if (navbar_style === 'Dark') {
						if (!(frm.doc.js || '').includes(`.addClass('navbar-dark bg-dark')`)) {
							js_lines.push(
								`frappe.ready(() => {`,
								`\t$('.navbar').removeClass('navbar-light bg-white').addClass('navbar-dark bg-dark')`,
								`})`
							);
						}
					}

					scss_lines.push(
						`@import "frappe/public/scss/website";`,
						'\n'
					);

					// set scss
					frm.set_value('theme_scss', scss_lines.join('\n'));

					// set js
					const js = frm.doc.js || '';
					frm.set_value('js', js_lines.join('\n') + js);

					d.hide();
				}
			});

			if (frm.doc.theme_scss) {
				frappe.confirm(__('This will reset your current theme, are you sure you want to continue?'), () => {
					d.show();
				});
			} else {
				d.show();
			}
		});

		if (!frm.doc.custom && !frappe.boot.developer_mode) {
			frm.set_read_only();
			frm.disable_save();
		} else {
			frm.enable_save();
		}
	}
});
