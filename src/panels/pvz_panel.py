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
        previz_scene.render.engine = 'BLENDER_EEVEE'
        
        # 4. Ativar modo rendered no viewport
        view3d_area = None
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                view3d_area = area
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'RENDERED'
                break
        
        # 5. Ativar Focus Mode (maximizar 3D Viewport)
        if view3d_area:
            # Temporariamente mudar o contexto para a área 3D View
            override = context.copy()
            override['area'] = view3d_area
            override['region'] = view3d_area.regions[-1]
            
            # Ativar o focus mode (tela cheia da área)
            with context.temp_override(**override):
                bpy.ops.screen.screen_full_area()
        
        self.report({'INFO'}, "Modo Previz ativado com Focus Mode")
        return {'FINISHED'}


class PVZ_OT_exit_previz_mode(Operator):
    """Sair do modo Previz e voltar para a cena anterior"""
    bl_idname = "pvz.exit_previz_mode"
    bl_label = "Sair do Modo Previz"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Desativar Focus Mode se estiver ativo
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                override = context.copy()
                override['area'] = area
                override['region'] = area.regions[-1]
                
                # Verificar se está em full screen e desativar
                if context.screen.show_fullscreen:
                    with context.temp_override(**override):
                        bpy.ops.screen.screen_full_area()
                break
        
        # Voltar para a primeira cena que não seja "Previz"
        for scene in bpy.data.scenes:
            if scene.name != "Previz":
                context.window.scene = scene
                self.report({'INFO'}, f"Voltou para cena: {scene.name}")
                return {'FINISHED'}
        
        self.report({'WARNING'}, "Nenhuma outra cena disponível")
        return {'CANCELLED'}


class PVZ_PT_main_panel(Panel):
    """Painel principal do Previz Mode"""
    bl_label = "PREVIZ MODE"
    bl_idname = "PVZ_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PREVIZ MODE'
    
    def draw(self, context):
        layout = self.layout
        
        # Verificar se está na cena Previz
        is_previz = context.scene.name == "Previz"
        
        # Botão principal
        row = layout.row()
        row.scale_y = 2.0
        
        if not is_previz:
            row.operator("pvz.toggle_previz_mode", 
                        text="ATIVAR PREVIZ", 
                        icon='SHADING_RENDERED')
        else:
            row.operator("pvz.exit_previz_mode", 
                        text="SAIR DO PREVIZ", 
                        icon='BACK')
        
        # Informações da cena atual
        layout.separator()
        box = layout.box()
        box.label(text="Cena Atual:", icon='SCENE_DATA')
        box.label(text=f"  {context.scene.name}")
        box.label(text="Engine:", icon='RESTRICT_RENDER_OFF')
        box.label(text=f"  {context.scene.render.engine}")
        
        # Status do Focus Mode
        if context.screen.show_fullscreen:
            box.label(text="Focus Mode: ATIVO", icon='FULLSCREEN_ENTER')
        else:
            box.label(text="Focus Mode: INATIVO", icon='FULLSCREEN_EXIT')


classes = (
    PVZ_OT_toggle_previz_mode,
    PVZ_OT_exit_previz_mode,
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