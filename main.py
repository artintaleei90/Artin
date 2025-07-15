<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>فروشگاه هالستون</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <h1>فروشگاه هالستون</h1>
    <button id="cart-button">🛒 سبد خرید <span id="cart-count">0</span></button>
  </header>

  <main id="product-list"></main>

  <div id="cart-modal" class="modal hidden">
    <div class="modal-content">
      <span class="close-button" id="close-cart">&times;</span>
      <h2>سبد خرید</h2>
      <ul id="cart-items"></ul>

      <h3>اطلاعات مشتری</h3>
      <input type="text" id="name" placeholder="نام">
      <input type="text" id="phone" placeholder="شماره تماس">
      <input type="text" id="city" placeholder="شهر">
      <textarea id="address" placeholder="آدرس کامل"></textarea>

      <button id="submit-order">🧾 ثبت سفارش</button>
    </div>
  </div>

  <script src="script.js"></script>
</body>
</html>
