export default function update_gauge(gauge_id, new_val) {
    let gauge = document.getElementById(gauge_id)
    let angle = Math.min((new_val / 100), 1) * 180

    gauge.style.rotate = `${180 + angle}deg`
}