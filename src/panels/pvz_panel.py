import bpy
from bpy.types import Panel, Operator


class PVZ_OT_toggle_previz_mode(Operator):
    """Alterna para o modo Previz"""
    bl_idname = "pvz.toggle_previz_mode"
    bl_label = "Ativar Modo Previz"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # 1. Verificar se existe cena "Previz", se não, criar
        previz_scene = bpy.data.scenes.get("Previz")
        
        if previz_scene is None:
            # Criar nova cena baseada na atual
            current_scene = context.scene
            previz_scene = bpy.data.scenes.new("Previz")
            
            # Copiar configurações básicas
            previz_scene.camera = current_scene.camera
            previz_scene.world = current_scene.world
            
            # Copiar objetos da cena atual
            for obj in current_scene.objects:
                previz_scene.collection.objects.link(obj)
            
            self.report({'INFO'}, "Cena Previz criada")
        
        # 2. Mudar para a cena Previz
        context.window.scene = previz_scene
        
        # 3. Mudar render engine para EEVEE
        previz_scene.render.engine = 'BLENDER_EEVEE_NEXT'
        
        # 4. Ativar modo rendered no viewport
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'RENDERED'
        
        self.report({'INFO'}, "Modo Previz ativado")
        return {'FINISHED'}


class PVZ_PT_main_panel(Panel):
    """Painel principal do Previz Mode"""
    bl_label = "PREVIZ MODE"
    bl_idname = "PVZ_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PREVIZ MODE'
    
    def draw(self, context):
        layout = self.layout
        
        # Botão principal
        row = layout.row()
        row.scale_y = 2.0
        row.operator("pvz.toggle_previz_mode", 
                     text="ATIVAR PREVIZ", 
                     icon='SHADING_RENDERED')
        
        # Informações da cena atual
        layout.separator()
        box = layout.box()
        box.label(text="Cena Atual:", icon='SCENE_DATA')
        box.label(text=f"  {context.scene.name}")
        box.label(text="Engine:", icon='RESTRICT_RENDER_OFF')
        box.label(text=f"  {context.scene.render.engine}")


classes = (
    PVZ_OT_toggle_previz_mode,
    PVZ_PT_main_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()