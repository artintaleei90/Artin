const products = [
  {
    code: "1101",
    name: "مانتو طرحدار بلند",
    price: 697000,
    image: "https://via.placeholder.com/200x200?text=محصول+1"
  },
  {
    code: "1102",
    name: "ست تابستانی چهارخونه",
    price: 547000,
    image: "https://via.placeholder.com/200x200?text=محصول+2"
  },
  {
    code: "1103",
    name: "کت و دامن زنانه مشکی",
    price: 747000,
    image: "https://via.placeholder.com/200x200?text=محصول+3"
  }
];

const cart = [];

function renderProducts() {
  const container = document.getElementById('product-list');
  container.innerHTML = '';
  products.forEach((product, index) => {
    const div = document.createElement('div');
    div.className = 'product';
    div.innerHTML = `
      <img src="${product.image}" alt="${product.name}">
      <h3>${product.name}</h3>
      <p>${product.price.toLocaleString()} تومان</p>
      <button onclick="addToCart(${index})">➕ افزودن به سبد خرید</button>
    `;
    container.appendChild(div);
  });
}

function addToCart(index) {
  const existing = cart.find(item => item.code === products[index].code);
  if (existing) {
    existing.count++;
  } else {
    cart.push({ ...products[index], count: 1 });
  }
  updateCartCount();
}

function updateCartCount() {
  document.getElementById('cart-count').textContent = cart.reduce((sum, i) => sum + i.count, 0);
}

document.getElementById('cart-button').onclick = () => {
  document.getElementById('cart-modal').classList.remove('hidden');
  renderCart();
};

document.getElementById('close-cart').onclick = () => {
  document.getElementById('cart-modal').classList.add('hidden');
};

function renderCart() {
  const ul = document.getElementById('cart-items');
  ul.innerHTML = '';
  cart.forEach(item => {
    const li = document.createElement('li');
    li.textContent = `${item.name} × ${item.count} = ${(item.price * item.count).toLocaleString()} تومان`;
    ul.appendChild(li);
  });
}

document.getElementById('submit-order').onclick = async () => {
  const name = document.getElementById('name').value.trim();
  const phone = document.getElementById('phone').value.trim();
  const city = document.getElementById('city').value.trim();
  const address = document.getElementById('address').value.trim();

  if (!name || !phone || !city || !address || cart.length === 0) {
    alert("لطفاً تمام فیلدها را پر کنید و حداقل یک محصول انتخاب کنید.");
    return;
  }

  if (!window.Telegram.WebApp || !window.Telegram.WebApp.initDataUnsafe) {
    alert("این برنامه فقط داخل تلگرام کار می‌کند.");
    return;
  }

  const chat_id = window.Telegram.WebApp.initDataUnsafe.user.id;

  const data = {
    name,
    phone,
    city,
    address,
    chat_id,
    orders: cart.map(i => ({
      code: i.code,
      name: i.name,
      price: i.price,
      count: i.count
    }))
  };

  try {
    const res = await fetch('/webapp/order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const result = await res.json();

    if (result.status === 'success') {
      alert("سفارش شما با موفقیت ثبت شد ✅");
      document.getElementById('cart-modal').classList.add('hidden');
      cart.length = 0;  // پاک کردن سبد خرید
      updateCartCount();
      clearForm();
    } else {
      alert("خطا در ثبت سفارش: " + result.message);
    }
  } catch (err) {
    alert("خطایی در ارسال سفارش رخ داد.");
  }
};

function clearForm() {
  document.getElementById('name').value = '';
  document.getElementById('phone').value = '';
  document.getElementById('city').value = '';
  document.getElementById('address').value = '';
}

renderProducts();
