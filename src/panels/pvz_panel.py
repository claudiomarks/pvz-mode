import bpy
from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import StringProperty, CollectionProperty, IntProperty


class PVZ_CameraItem(PropertyGroup):
    """Item de câmera para a lista"""
    name: StringProperty(name="Camera Name")
    obj_name: StringProperty(name="Object Name")


class PVZ_OT_toggle_previz_mode(Operator):
    """Alterna para o modo Previz"""
    bl_idname = "pvz.toggle_previz_mode"
    bl_label = "Ativar Modo Previz"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        pvz_props = scene.pvz_properties
        
        # Verificar se existe uma câmera selecionada
        if pvz_props.camera_index >= 0 and pvz_props.camera_index < len(pvz_props.cameras):
            selected_camera_name = pvz_props.cameras[pvz_props.camera_index].obj_name
            selected_camera = bpy.data.objects.get(selected_camera_name)
            
            if selected_camera is None:
                self.report({'ERROR'}, f"Câmera '{selected_camera_name}' não encontrada")
                return {'CANCELLED'}
        else:
            self.report({'ERROR'}, "Nenhuma câmera selecionada")
            return {'CANCELLED'}
        
        # 1. Verificar se existe cena "Previz", se não, criar
        previz_scene = bpy.data.scenes.get("Previz")
        
        if previz_scene is None:
            # Criar nova cena baseada na atual
            current_scene = context.scene
            previz_scene = bpy.data.scenes.new("Previz")
            
            # Copiar configurações básicas
            previz_scene.world = current_scene.world
            
            # Copiar objetos da cena atual
            for obj in current_scene.objects:
                previz_scene.collection.objects.link(obj)
            
            self.report({'INFO'}, "Cena Previz criada")
        
        # 2. Definir a câmera selecionada como ativa na cena Previz
        previz_scene.camera = selected_camera
        
        # 3. Mudar para a cena Previz
        context.window.scene = previz_scene
        
        # 4. Mudar render engine para EEVEE
        previz_scene.render.engine = 'BLENDER_EEVEE'
        
        # 5. Ativar modo rendered no viewport e entrar na visão da câmera
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                space = area.spaces.active
                if space.type == 'VIEW_3D':
                    space.shading.type = 'RENDERED'
                    # Entrar na visão da câmera diretamente
                    space.region_3d.view_perspective = 'CAMERA'
                break
        
        # 6. Ativar Focus Mode (fullscreen da área 3D)
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                with context.temp_override(area=area):
                    bpy.ops.screen.screen_full_area()
                break
        
        self.report({'INFO'}, f"Modo Previz ativado com câmera: {selected_camera.name}")
        return {'FINISHED'}


class PVZ_OT_toggle_fly_mode(Operator):
    """Ativa/Desativa modo de navegação WASD (Fly Mode)"""
    bl_idname = "pvz.toggle_fly_mode"
    bl_label = "Toggle Fly Mode"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Encontrar a área 3D View e a região
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                space = area.spaces.active
                for region in area.regions:
                    if region.type == 'WINDOW':
                        override = {
                            'area': area,
                            'region': region,
                            'space_data': space,
                        }
                        with context.temp_override(**override):
                            # Tentar fly mode primeiro, se não funcionar tenta walk
                            try:
                                bpy.ops.view3d.fly('INVOKE_DEFAULT')
                            except:
                                bpy.ops.view3d.walk('INVOKE_DEFAULT')
                        break
                break
        
        return {'FINISHED'}


class PVZ_OT_exit_previz_mode(Operator):
    """Sair do modo Previz e voltar para a cena anterior"""
    bl_idname = "pvz.exit_previz_mode"
    bl_label = "Sair do Modo Previz"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Primeiro sair da visão da câmera se estiver nela
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                space = area.spaces.active
                if space.type == 'VIEW_3D':
                    if space.region_3d.view_perspective == 'CAMERA':
                        space.region_3d.view_perspective = 'PERSP'
                break
        
        # Depois desativar Focus Mode se estiver ativo
        if context.screen.show_fullscreen:
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    with context.temp_override(area=area):
                        bpy.ops.screen.screen_full_area()
                    break
        
        # Por último, voltar para a primeira cena que não seja "Previz"
        for scene in bpy.data.scenes:
            if scene.name != "Previz":
                context.window.scene = scene
                self.report({'INFO'}, f"Voltou para cena: {scene.name}")
                return {'FINISHED'}
        
        self.report({'WARNING'}, "Nenhuma outra cena disponível")
        return {'CANCELLED'}


class PVZ_OT_switch_camera(Operator):
    """Troca para a câmera selecionada"""
    bl_idname = "pvz.switch_camera"
    bl_label = "Trocar Câmera"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        pvz_props = scene.pvz_properties
        
        # Verificar se existe uma câmera selecionada
        if pvz_props.camera_index >= 0 and pvz_props.camera_index < len(pvz_props.cameras):
            selected_camera_name = pvz_props.cameras[pvz_props.camera_index].obj_name
            selected_camera = bpy.data.objects.get(selected_camera_name)
            
            if selected_camera is None:
                self.report({'ERROR'}, f"Câmera '{selected_camera_name}' não encontrada")
                return {'CANCELLED'}
            
            # Trocar câmera ativa da cena
            scene.camera = selected_camera
            
            # Se estiver na visão de câmera, forçar atualização
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    space = area.spaces.active
                    if space.type == 'VIEW_3D':
                        if space.region_3d.view_perspective == 'CAMERA':
                            # Força atualização da viewport
                            area.tag_redraw()
                    break
            
            self.report({'INFO'}, f"Câmera trocada para: {selected_camera.name}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Nenhuma câmera selecionada")
            return {'CANCELLED'}


class PVZ_OT_refresh_cameras(Operator):
    """Atualiza a lista de câmeras da collection POV"""
    bl_idname = "pvz.refresh_cameras"
    bl_label = "Atualizar Câmeras"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        pvz_props = scene.pvz_properties
        
        # Limpar lista atual
        pvz_props.cameras.clear()
        
        # Verificar se existe a collection POV
        pov_collection = bpy.data.collections.get("POV")
        
        if pov_collection is None:
            self.report({'WARNING'}, "Collection 'POV' não encontrada")
            return {'CANCELLED'}
        
        # Buscar câmeras na collection POV
        camera_count = 0
        for obj in pov_collection.objects:
            if obj.type == 'CAMERA':
                item = pvz_props.cameras.add()
                item.name = obj.name
                item.obj_name = obj.name
                camera_count += 1
        
        # Selecionar a primeira câmera por padrão
        if camera_count > 0:
            pvz_props.camera_index = 0
            self.report({'INFO'}, f"{camera_count} câmera(s) encontrada(s)")
        else:
            self.report({'WARNING'}, "Nenhuma câmera encontrada na collection 'POV'")
        
        return {'FINISHED'}


class PVZ_UL_camera_list(bpy.types.UIList):
    """Lista de câmeras"""
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon='CAMERA_DATA')
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon='CAMERA_DATA')


class PVZ_Properties(PropertyGroup):
    """Propriedades do addon"""
    cameras: CollectionProperty(type=PVZ_CameraItem)
    camera_index: IntProperty(default=0)


class PVZ_PT_main_panel(Panel):
    """Painel principal do Previz Mode"""
    bl_label = "PREVIZ MODE"
    bl_idname = "PVZ_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PREVIZ MODE'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        pvz_props = scene.pvz_properties
        
        # Seção de Câmeras
        box = layout.box()
        box.label(text="Câmeras POV:", icon='OUTLINER_OB_CAMERA')
        
        row = box.row()
        row.template_list(
            "PVZ_UL_camera_list", "",
            pvz_props, "cameras",
            pvz_props, "camera_index",
            rows=3
        )
        
        row = box.row()
        row.operator("pvz.refresh_cameras", icon='FILE_REFRESH')
        
        # Botão para trocar câmera
        if len(pvz_props.cameras) > 0:
            row = box.row()
            row.scale_y = 1.3
            row.operator("pvz.switch_camera", text="TROCAR CÂMERA", icon='CAMERA_DATA')
        
        # Mostrar câmera selecionada
        if pvz_props.camera_index >= 0 and len(pvz_props.cameras) > 0:
            if pvz_props.camera_index < len(pvz_props.cameras):
                selected_cam = pvz_props.cameras[pvz_props.camera_index]
                box.label(text=f"Selecionada: {selected_cam.name}", icon='OUTLINER_OB_CAMERA')
        
        layout.separator()
        
        # Verificar se está na cena Previz
        is_previz = context.scene.name == "Previz"
        
        # Botão principal
        row = layout.row()
        row.scale_y = 2.0
        
        if not is_previz:
            row.operator("pvz.toggle_previz_mode", 
                        text="ATIVAR PREVIZ", 
                        icon='SHADING_RENDERED')
            # Desabilitar botão se não houver câmera selecionada
            row.enabled = len(pvz_props.cameras) > 0
        else:
            row.operator("pvz.exit_previz_mode", 
                        text="SAIR DO PREVIZ", 
                        icon='BACK')
        
        # Botão Fly Mode (navegação WASD)
        if is_previz:
            layout.separator()
            row = layout.row()
            row.scale_y = 1.5
            row.operator("pvz.toggle_fly_mode", 
                        text="NAVEGAÇÃO WASD", 
                        icon='VIEW_PAN')


classes = (
    PVZ_CameraItem,
    PVZ_Properties,
    PVZ_OT_toggle_previz_mode,
    PVZ_OT_toggle_fly_mode,
    PVZ_OT_exit_previz_mode,
    PVZ_OT_switch_camera,
    PVZ_OT_refresh_cameras,
    PVZ_UL_camera_list,
    PVZ_PT_main_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Registrar propriedades na cena
    bpy.types.Scene.pvz_properties = bpy.props.PointerProperty(type=PVZ_Properties)


def unregister():
    # Remover propriedades da cena
    del bpy.types.Scene.pvz_properties
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()