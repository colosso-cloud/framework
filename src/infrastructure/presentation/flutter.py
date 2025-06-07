import flet as ft
import flet_video as fv
import importlib
import asyncio
import tinycss2

modules = {'flow': 'framework.service.flow','presentation': 'framework.port.presentation'}


CSS_TO_FLET = {
    "background-color": "bgcolor",
    "color": "color",
    "padding": "padding",
    "border-radius": "border_radius",
}

MAPPA = {
    "background-color": {'css':'bgcolor'},
    "color": {'css':'color'},
    "padding": {'css':'padding'},
    "border-radius": {'css':'border_radius'},
}

COLOR_MAP = {
    "white": ft.Colors.WHITE,
    "blue": ft.Colors.BLUE,
    "red": ft.Colors.RED,
    "black": ft.Colors.BLACK,
    "green": ft.Colors.GREEN,
    # Aggiungi altri colori se servono
}

def convert_value(prop, val):
    if val.endswith("px"):
        return int(val.replace("px", "").strip())
    if val.lower() in COLOR_MAP:
        return COLOR_MAP[val.lower()]
    return val

def parse_css_tinycss2(css_text):
    rules = tinycss2.parse_stylesheet(css_text, skip_whitespace=True)
    styles = {}

    for rule in rules:
        if rule.type != "qualified-rule":
            continue

        selector_raw = "".join([t.serialize() for t in rule.prelude]).strip()
        selectors = [s.strip() for s in selector_raw.split(",")]

        declarations = tinycss2.parse_declaration_list(rule.content)
        style_dict = {}

        for decl in declarations:
            if decl.type != "declaration":
                continue
            name = decl.name.strip()
            value = "".join([v.serialize() for v in decl.value if hasattr(v, "serialize")]).strip()
            if name in CSS_TO_FLET:
                prop = CSS_TO_FLET[name]
                style_dict[prop] = convert_value(prop, value)

        for selector in selectors:
            parts = selector.replace(".", " .").replace("#", " #").split()
            for part in parts:
                if part.startswith("."):
                    key = f"class:{part[1:]}"
                elif part.startswith("#"):
                    key = f"id:{part[1:]}"
                else:
                    key = f"tag:{part}"
                styles.setdefault(key, {}).update(style_dict)

    return styles

class adapter(presentation.port):

    @flow.asynchronous()
    async def attribute_id(self, widget, pr, value):
        self.document[value] = widget
        widget.id = value

    async def attribute_name(self, widget, pr, value): widget.name = value

    async def attribute_tooltip(self, widget, pr, value): widget.tooltip = value

    async def attribute_placeholder(self, widget, pr, value): widget.hint_text = value

    async def attribute_value(self, widget, pr, value): widget.value = value

    async def attribute_state(self, widget, pr, value):
        if value == "readonly":
            widget.read_only = True
        elif value == "disabled":
            widget.disabled = True
        elif value == "selected":
            widget.selected = True
        elif value == "enabled":
            widget.enabled = True

    
    @flow.asynchronous(managers=('executor',))
    async def attribute_click(self, widget, pr, value, executor):
        async def on_click(e):
            await executor.act(action=value)
        
        widget.on_click = on_click

    async def attribute_change(self, widget, pr, value): widget.on_change = value

    async def attribute_route(self, widget, pr, value): widget.route = value

    async def attribute_init(self, widget, pr, value): widget.on_init = value

    async def attribute_width(self, widget, pr, value): widget.width = int(value)

    async def attribute_height(self, widget, pr, value): widget.height = int(value)

    async def attribute_space(self, widget, pr, value): widget.spacing = value

    async def attribute_expand(self, widget, pr, value):
        if value == "fill":
            widget.expand = True
        elif value == "vertical":
            widget.height = ft.MainAxisSize.MAX
        elif value == "horizontal":
            widget.width = ft.MainAxisSize.MAX
        else:
            widget.expand = False

    async def attribute_collapse(self, widget, pr, value): widget.collapse = value

    async def attribute_border(self, widget, pr, value): widget.border = value

    async def attribute_border_top(self, widget, pr, value): widget.border_top = value

    async def attribute_border_bottom(self, widget, pr, value): widget.border_bottom = value

    async def attribute_border_left(self, widget, pr, value): widget.border_left = value

    async def attribute_border_right(self, widget, pr, value): widget.border_right = value

    async def attribute_margin(self, widget, pr, value): widget.margin = value

    async def attribute_margin_top(self, widget, pr, value): widget.margin_top = value

    async def attribute_margin_bottom(self, widget, pr, value): widget.margin_bottom = value

    async def attribute_margin_left(self, widget, pr, value): widget.margin_left = value

    async def attribute_margin_right(self, widget, pr, value): widget.margin_right = value

    async def attribute_padding(self, widget, pr, value): widget.padding = int(value)

    async def attribute_padding_top(self, widget, pr, value): widget.padding_top = value

    async def attribute_padding_bottom(self, widget, pr, value): widget.padding_bottom = value

    async def attribute_padding_left(self, widget, pr, value): widget.padding_left = value

    async def attribute_padding_right(self, widget, pr, value): widget.padding_right = value

    async def attribute_size(self, widget, pr, value): widget.size = value

    async def attribute_alignment_horizontal(self, widget, pr, value): widget.alignment_horizontal = value

    async def attribute_alignment_vertical(self, widget, pr, value): widget.alignment_vertical = value

    async def attribute_alignment_content(self, widget, pr, value): widget.alignment_content = value

    async def attribute_position(self, widget, pr, value): widget.position = value

    async def attribute_style(self, widget, pr, value): widget.style = value

    async def attribute_shadow(self, widget, pr, value): widget.shadow = value

    async def attribute_opacity(self, widget, pr, value): widget.opacity = float(value)

    async def attribute_background_color(self, widget, pr, value): widget.bgcolor = value

    async def attribute_class(self, widget, pr, value): widget.class_name = value  # "class" is reserved

    async def set_attribute(self, widget, pr, value): 
        widget.class_name = value  # "class" is reserved

    async def get_attribute(self, widget, field, value=None):
        match field:
            case 'elements':
                a = getattr(widget,'controls',None)
                if a:
                    return a
                a = getattr(widget,'content',None)
                if a:
                    return await self.get_attribute(a,'elements')
            case 'class':
                return getattr(widget,'class_name',None)
            case _:
                return getattr(widget,field,None)

    async def selector(self, **constants):
        for key in constants:
            value = constants[key]
            match key:
                case 'id':
                    return [self.document[value]]
        

    def __init__(self,**constants):
        self.tree_view = dict()
        self.config = constants['config']
        
        self.initialize()
        async def main(page: ft.Page):
            #page.window_title_bar_hidden = True
            #page.window_title_bar_buttons_hidden = True
            #page.title = self.config['title']
            aaa = await self.host({'url':self.config.get('view')})
            
            page.vertical_alignment = ft.MainAxisAlignment.CENTER
            page.spacing = 0
            page.margin=0
            page.padding=0
            #print(self.builder)
            view = await self.builder(text=aaa)
            #print('VIEW',view)
            #await page.add_async(view,)
            page.add(view)
        asyncio.create_task(ft.app_async(main))

    @staticmethod
    def widget_button(tag, inner, props):
        variant = props.get("variant", "text")
        if variant == "icon":
            widget = ft.IconButton(
                icon=props.get("icon", ft.icons.PLAY_ARROW),
                icon_size=props.get("icon_size", 24),
                on_click=props.get("on_click"),
            )
        widget = ft.TextButton(
            text=props.get("text", "Click Me"),
            on_click=props.get("on_click"),
        )
    
        widget.tag = tag
        return widget

    @staticmethod
    def widget_video(tag, inner, props):
        widget = fv.Video(playlist=inner)
        widget.tag = tag
        return widget

    @staticmethod
    def widget_videomedia(tag, inner, props):
        widget = fv.VideoMedia(inner)
        widget.tag = tag
        return widget
    
    @staticmethod
    def widget_column(tag, inner, props):
        print(inner)
        widget = ft.Column(controls=inner)
        widget.tag = tag
        return widget
    
    @staticmethod
    def widget_row(tag, inner, props):
        print('Row',inner)
        widget = ft.Row(controls=inner)
        widget.tag = tag
        return widget
    
    @staticmethod
    def widget_container(tag, inner, props):
        print('Container',inner,props)
        widget = ft.Container(content=ft.ResponsiveRow(expand=True,controls=inner))
        widget.tag = tag
        return widget
    
    
    def widget_button(self, tag, inner, props):
        print('Button',inner)
        widget = ft.FilledButton(content=ft.ResponsiveRow(expand=True,controls=inner))
        widget.tag = tag
        return widget
    
    @staticmethod
    def widget_text(tag, inner, props):
        print('Text',inner)
        text = ''
        for x in inner:
            if type(x) == type(''):
                text += x
                inner.remove(x)

        widget = ft.Text(value=text)
        widget.tag = tag
        return widget
    
    @staticmethod
    def widget_input(tag, inner, props):
        print('Input',inner,props)
        ttype = props.get('type','text')
        match ttype:
            case 'text':
                widget = ft.TextField()
            case 'password':
                widget = ft.TextField(password=True, can_reveal_password=True)
            case _:
                widget = ft.TextField()
        
        widget.tag = tag
        return widget
    
    
    async def mount_route(self, *services, **constants):
        pass

    
    async def render_view(self, *services, **constants):
        pass

    async def apply_style(self ,widget, styles=None):
        if styles is None:
            return
        applied = {}
        tag = await self.get_attribute(widget,'tag')
        id = await self.get_attribute(widget,'id')
        classes = await self.get_attribute(widget,'class')
        
        # Applica per tag (es: button)
        if tag and f"tag:{tag}" in styles:
            applied.update(styles[f"tag:{tag}"])

        # Applica per classi
        if classes:
            classes = classes.split(' ')
            for cls in classes:
                key = f"class:{cls}"
                if key in styles:
                    applied.update(styles[key])

        # Applica per ID
        if id and f"id:{id}" in styles:
            applied.update(styles[f"id:{id}"])

        # Imposta attributi sul widget
        for attr, val in applied.items():
            setattr(widget, attr, val)

    async def mount_css(self, *services, **constants):
        ttt = """
.primary {
  background-color: #ff0000;
  color: white;
  padding: 10px;
  border-radius: 0px;
}

Container {
  background-color: red;
  color: white;
  padding: 12px;
  border-radius: 4px;
}
"""
        styles = parse_css_tinycss2(ttt)
        #print('style:',styles)
        for key in self.document:
            widget = self.document[key]
            await self.apply_style(widget, styles)
                
        