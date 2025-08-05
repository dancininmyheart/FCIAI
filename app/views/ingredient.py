import os
import json
from flask import Blueprint, request, jsonify, current_app, url_for, send_file
from flask_login import login_required

ingredient = Blueprint('ingredient', __name__)

# 缓存JSON数据
_cached_data = None
_cache_file_path = None

def load_ingredient_data():
    """加载保健食品注册数据"""
    global _cached_data, _cache_file_path
    
    # 获取JSON文件路径
    json_file_path = os.path.join(current_app.root_path, 'Ingredient_Search', '保健食品注册.json')
    json_file_path = os.path.abspath(json_file_path)
    
    # 如果已经缓存且文件未修改，则直接返回缓存数据
    if _cached_data and _cache_file_path == json_file_path:
        return _cached_data
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            _cached_data = json.load(f)
            _cache_file_path = json_file_path
            return _cached_data
    except Exception as e:
        print(f"加载JSON文件失败: {str(e)}")
        return {}


def get_image_url(image_path):
    """将本地图片路径转换为可访问的URL"""
    if not image_path or image_path == '无截图路径':
        return None
    
    # 如果是相对路径，转换为相对于应用根目录的路径
    if not os.path.isabs(image_path):
        # 将路径分隔符统一为正斜杠
        image_path = image_path.replace('\\', '/')
        # 构造URL路径
        return f"/ingredient/image/{image_path}"
    
    return None


@ingredient.route('/api/ingredient/search', methods=['GET'])
@login_required
def search_ingredient():
    """搜索保健食品成分API"""
    try:
        # 获取查询参数
        keyword = request.args.get('keyword', '').strip()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 12))  # 默认每页12个结果
        
        # 参数验证
        if not keyword:
            return jsonify({
                'success': False,
                'message': '请输入搜索关键词'
            }), 400
        
        # 加载数据
        data = load_ingredient_data()
        if not data:
            return jsonify({
                'success': False,
                'message': '数据加载失败'
            }), 500
        
        # 搜索匹配的产品
        matched_products = []
        for product_name, product_info in data.items():
            ingredients = product_info.get('ingredient', '')
            
            # 检查关键词是否出现在成分列表中（不区分大小写）或产品名称中
            if keyword.lower() in ingredients.lower() or keyword.lower() in product_name.lower():
                # 提取主要成分（最多前3个）
                if ingredients:
                    main_ingredients = [ing.strip() for ing in ingredients.split(',')[:3]]
                    main_ingredients_str = "、".join(main_ingredients) + ("等" if len(ingredients.split(',')) > 3 else "")
                else:
                    main_ingredients_str = "无成分信息"
                
                # 获取图片URL
                image_path = product_info.get('path', '无截图路径')
                image_url = get_image_url(image_path) if image_path != '无截图路径' else None
                
                matched_products.append({
                    '产品名称': product_name,
                    '主要成分': main_ingredients_str,
                    '完整成分': ingredients,
                    '截图路径': image_path,
                    '图片URL': image_url
                })
        
        # 分页处理
        total = len(matched_products)
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        paginated_products = matched_products[start_index:end_index]
        
        # 返回结果
        return jsonify({
            'success': True,
            'data': paginated_products,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        print(f"搜索出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'搜索出错: {str(e)}'
        }), 500


@ingredient.route('/image/<path:image_path>')
@login_required
def serve_ingredient_image(image_path):
    """提供成分图片访问"""
    try:
        # 构造完整的图片路径
        full_image_path = os.path.join(current_app.root_path, '..', 'Ingredient_Search', image_path)
        full_image_path = os.path.abspath(full_image_path)
        
        # 检查文件是否存在
        if not os.path.exists(full_image_path):
            return jsonify({'error': '图片不存在'}), 404
        
        # 返回图片文件
        return send_file(full_image_path)
    except Exception as e:
        print(f"提供图片出错: {str(e)}")
        return jsonify({'error': '无法提供图片'}), 500


@ingredient.route('/api/ingredient/download/<path:image_path>')
@login_required
def download_ingredient_image(image_path):
    """下载成分图片"""
    # print("触发下载！")
    try:
        # 构造完整的图片路径
        # print(image_path)
        image_path=image_path.replace("data","data\\")
        full_image_path = os.path.join(current_app.root_path, 'Ingredient_Search', image_path)
        # print(full_image_path)
        full_image_path = os.path.abspath(full_image_path)
        
        # 检查文件是否存在
        if not os.path.exists(full_image_path):
            return jsonify({'error': '图片不存在'}), 404
        
        # 获取文件名
        filename = os.path.basename(full_image_path)
        
        # 返回图片文件供下载
        return send_file(full_image_path, as_attachment=True, download_name=filename)
    except Exception as e:
        print(f"下载图片出错: {str(e)}")
        return jsonify({'error': f'无法下载图片: {str(e)}'}), 500


# 导入send_from_directory
from flask import send_from_directory
