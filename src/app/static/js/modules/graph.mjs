const MAX_HEIGHT = 10
const GRAPH_FLOOR = 0 
const TODAY = Date.now()
const STROKE_COLOR = "#24b811"

export function sync_canvas_size(canvas) {
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();

    const displayWidth = Math.round(rect.width * dpr);
    const displayHeight = Math.round(rect.height * dpr);

    if (canvas.width !== displayWidth || canvas.height !== displayHeight) {
        canvas.width = displayWidth;
        canvas.height = displayHeight;
    }

    const context = canvas.getContext("2d");
    context.setTransform(dpr, 0, 0, dpr, 0, 0);

    return { context, width: rect.width, height: rect.height };
}

export default function draw_points(canvas, points, max_value, attribute_selector= (x) => x, color=STROKE_COLOR) {    
    if (!points) return

    const {context, width, height} = sync_canvas_size(canvas)

    context.clearRect(0, 0, canvas.width, canvas.height);

    const x_scale_factor = width / (points.length-1)
    const y_scale_factor = height / max_value
    const canvas_floor = height
    
    context.lineWidth = 3
    context.strokeStyle = STROKE_COLOR

    let path = new Path2D()

    let prev_x = 0

    for (let point of points) {
        prev_x = point[0]
        path.lineTo(point[0] * x_scale_factor, height - (attribute_selector(point[1]) * y_scale_factor))
    }

    context.stroke(path)
}