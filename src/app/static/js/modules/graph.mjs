const MAX_HEIGHT = 10
const GRAPH_FLOOR = 0 
const TODAY = Date.now()
const STROKE_COLOR = "#24b811"

function syncCanvasSize(canvas) {
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;

    canvas.width = Math.round(rect.width * dpr);
    canvas.height = Math.round(rect.height * dpr);

    const ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}

export default function draw_points(canvas, points, attribute_selector= (x) => x, color=STROKE_COLOR) {    
    if (!points) return

    syncCanvasSize(canvas)

    const rect =  canvas.getBoundingClientRect()

    const HEIGHT = rect.height
    const WIDTH = rect.width

    const x_scale_factor = WIDTH / (points.length-1)
    const canvas_floor = HEIGHT

    let context = canvas.getContext("2d")
    context.lineWidth = 3
    context.strokeStyle = STROKE_COLOR

    let path = new Path2D()    

    let prev_x = 0

    for (let point of points) {
        prev_x = point[0]
        path.lineTo(point[0] * x_scale_factor, HEIGHT - (attribute_selector(point[1]) * HEIGHT / 1.2))
    }

    context.stroke(path)
}