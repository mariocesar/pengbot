from collections import namedtuple


class TemplateBase:
    template_type = None
    _buttons = []

    @property
    def buttons(self):
        return self._buttons

    @buttons.setter
    def buttons(self, elements: list):
        self._buttons = elements

    def _asdict(self):
        payload = super()._asdict()
        payload['buttons'] = [dict(button) for button in self.buttons]
        return {
            'type': 'template',
            'payload': {
                'template_type': self.template_type,
                'elements': [payload]
            }
        }


class ButtonTemplate(TemplateBase, namedtuple('ButtonTemplate', ['text'])):
    template_type = 'button'

    def _asdict(self):
        payload = super()._asdict()
        payload['buttons'] = [dict(button) for button in self.buttons]
        payload['template_type'] = self.template_type,

        return {
            'type': 'template',
            'payload': payload
        }


class GenericTemplate(TemplateBase, namedtuple('GenericTemplate', ['title', 'item_url', 'image_url', 'subtitle'])):
    template_type = 'generic'

    def _asdict(self):
        payload = super()._asdict()
        payload['buttons'] = [dict(button) for button in self.buttons]
        return {
            'type': 'template',
            'payload': {
                'template_type': self.template_type,
                'elements': [payload]  # TODO, suppor up to 10 elements
            }
        }
