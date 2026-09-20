const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const GAME_WIDTH = canvas.width;
const GAME_HEIGHT = canvas.height;
let gameOver=false
const garbageTypes = [
    { symbol: "👢", width: 20, height: 20, weight: 1, points: 3 },
    { symbol: "🥫", width: 10, height: 10, weight: 2, points: 1 },
    { symbol: "🍾", width: 15, height: 15, weight: 3, points: 2 }
];
// to do: randomize and more garbage
const shark = {
    height: 30,
    width: 30,
    speed: 0.3,
    x: Math.floor(Math.random() * 1200),
    y: Math.floor(Math.random() * 600)
}
const garbage = [
    createGarbage(500, 200),
    createGarbage(250, 500),
    createGarbage(100, 75),
    createGarbage(700, 200)
];
const player = {
    x: 0,
    y: 200,
    width: 30,
    height: 30,
    speed: 5,
    velocityX: 0,
    velocityY: 0,
    acceleration: 0.5,
    friction: 0.85
};
let score = 0;
let lives = 3;
const keys = {};
document.addEventListener("keydown", function (e) {
    keys[e.key.toLowerCase()] = true;
});
function createGarbage(x, y) {
    const type = garbageTypes[
        Math.floor(Math.random() * garbageTypes.length)
    ];
    return {
        x: x,
        y: y,
        width: type.width,
        height: type.height,
        symbol: type.symbol,
        weight: type.weight,
        points: type.points
    };
}
function updateLives(){
    let hearts = ""
    for (let i = 0; i < lives; i ++){
        hearts += "❤️"
    }
    document.getElementById("lives").textContent=hearts
}
function endGame(){
    gameOver = true
    document.getElementById("finalScore").textContent=score
    document.getElementById("gameOver").classList.remove("hidden")
    saveScore()
}
function saveScore(){
    fetch ("/save_score", {
        method:"POST",
        headers:{
            "content-Type":"application/json"
        },
        body: JSON.stringify({name:playerName, score:score})
    })
}
document.addEventListener("keyup", function (e) {
    keys[e.key.toLowerCase()] = false;
});
function drawShark() {
    console.log(shark.x, shark.y)
    ctx.font = "50px Arial";
    ctx.fillText(
        "🦈",
        shark.x,
        shark.y + shark.height
    );
}
function moveShark() {
    if (shark.x < player.x){
        shark.x += shark.speed
    }
    if (shark.x > player.x){
        shark.x -= shark.speed
    }
    if (shark.y < player.y){
        shark.y += shark.speed
    }
    if (shark.y > player.y){
        shark.y -= shark.speed
    }
}
function checkSharkCollision() {
    if (isCollision(player, shark)){
        lives -= 1
        updateLives()
        shark.x = Math.floor(Math.random() * 1400)
        shark.y = Math.floor(Math.random() * 600)
        if (lives <= 0){
            endGame()
        }
    }
}
function movePlayer() {
    let directionX = 0;
    let directionY = 0;
    if (keys["a"]) directionX -= 1;
    if (keys["d"]) directionX += 1;
    if (keys["w"]) directionY -= 1;
    if (keys["s"]) directionY += 1;
    player.velocityX += directionX * player.acceleration;
    player.velocityY += directionY * player.acceleration;
    if (directionX === 0) {
        player.velocityX *= player.friction;
    }
    if (directionY === 0) {
        player.velocityY *= player.friction;
    }
    player.velocityX = Math.max(
        -player.speed,
        Math.min(player.speed, player.velocityX)
    );
    player.velocityY = Math.max(
        -player.speed,
        Math.min(player.speed, player.velocityY)
    );
    player.x += player.velocityX;
    player.y += player.velocityY;
    if (player.x < 0) {
        player.x = 0;
        player.velocityX = 0;
    }
    if (player.x + player.width > GAME_WIDTH) {
        player.x = GAME_WIDTH - player.width;
        player.velocityX = 0;
    }
    if (player.y < 0) {
        player.y = 0;
        player.velocityY = 0;
    }
    if (player.y + player.height > GAME_HEIGHT) {
        player.y = GAME_HEIGHT - player.height;
        player.velocityY = 0;
    }
}
function drawOcean() {
    ctx.fillStyle = "#087ea4";
    ctx.fillRect(0, 0, GAME_WIDTH, GAME_HEIGHT);
    ctx.font = "20px Arial";
    ctx.fillText("o", 100, 100);
    ctx.fillText("o", 300, 200);
    ctx.fillText("o", 700, 100);
    ctx.fillText("o", 500, 450);
}
function drawPlayer() {
    ctx.font = "30px Arial";
    ctx.fillText(
        "🤿",
        player.x,
        player.y + player.height
    );
}
function drawGarbage() {
    garbage.forEach(item => {
        ctx.font = `${item.width}px Arial`;
        ctx.fillText(
            item.symbol,
            item.x,
            item.y + item.height
        );
    });
}
function isCollision(a, b) {
    return (
        a.x < b.x + b.width &&
        a.x + a.width > b.x &&
        a.y < b.y + b.height &&
        a.y + a.height > b.y
    );
}
function checkGarbageCollision() {
    garbage.forEach((item, index) => {
        if (isCollision(player, item)) {
            score += item.points;
            document.getElementById("score").textContent = score;
            garbage.splice(index, 1);
        }
    });
}
function spawnGarbage() {
    const x = Math.random() * (GAME_WIDTH - 50);
    const y = Math.random() * (GAME_HEIGHT - 50);

    garbage.push(createGarbage(x, y));

    const delay =
        Math.floor(Math.random() * (15000 - 5000 + 1)) + 5000;

    setTimeout(spawnGarbage, delay);
}
spawnGarbage();
function gameLoop() {
    if (gameOver) {
        return;
    }
    ctx.clearRect(0, 0, GAME_WIDTH, GAME_HEIGHT);
    drawOcean();
    movePlayer();
    moveShark();
    drawPlayer();
    drawShark();
    drawGarbage();
    checkGarbageCollision();
    checkSharkCollision();
    requestAnimationFrame(gameLoop);
}
gameLoop();