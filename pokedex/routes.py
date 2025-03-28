from pokedex import app, db, bcrypt
from flask import render_template, request, url_for, redirect, flash
from pokedex.models import User, Pokemon, PokemonType
from flask_login import login_user, logout_user, current_user, login_required

@app.route('/')
def home():
  page = request.args.get('page', type=int)
  pokemons = db.paginate(db.select(Pokemon), per_page=4, page=page)
  return render_template('index.html', 
                         title='Home Page',
                         pokemons=pokemons)

@app.route('/detail/<int:id>/')
def detail(id):
  pokemon = db.session.get(Pokemon, id)
  return render_template('detail_pokemon.html',
                         title='Car\'s Detail Page',
                         pokemon=pokemon)


@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    username = request.form['username']
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    user = db.session.scalar(db.select(User).where(User.username==username))

    if user:
      flash('Username is already exists!', 'warning')
    else:
      user = db.session.scalar(db.select(User).where(User.email==email))
      if user:
        flash('Email is already exists!', 'warning')
      else:
        if password != confirm_password:
          flash('Password Not Match', 'warning')
        else:
          user = User(username=username,
                      email=email,
                      password=bcrypt.generate_password_hash(password))
          db.session.add(user)
          db.session.commit()

          return redirect(url_for('login'))

  return render_template('user/register.html',
                         title='Register Page')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    username = request.form.get('username')
    password = request.form['password']

    user = db.session.scalar(db.select(User).where(User.username==username))
    if user:
      if bcrypt.check_password_hash(user.password, password):
        login_user(user)
        return redirect(url_for('home'))
      
      else:
        flash('Password is invalid!', 'warning')
    else:
      flash('Username is not exists!', 'warning')

  return render_template('user/login.html',
                         title='Login Page')

@app.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
  if request.method == 'POST':
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    current_user.firstname = firstname
    current_user.lastname = lastname

    db.session.commit()
    flash('Update profile successful.', 'success')
    return redirect(url_for('profile'))
  
  return render_template('user/profile.html',
                         title='Profile Page')

@app.route('/pokemon/type', methods=['GET', 'POST'])
@login_required
def pokemon_types():
    # Check if there is a search query (using POST)
    search_query = request.form.get('type_name') if request.method == 'POST' else None
    
    # If there is a search query, filter the types based on the name
    if search_query:
        types = db.session.scalars(db.select(PokemonType).where(PokemonType.name.ilike(f'%{search_query}%'))).all()
    else:
        # If no search query, return all types
        types = db.session.scalars(db.select(PokemonType)).all()

    return render_template('type/index.html',
                           title='Car Model Page',
                           types=types)

@app.route('/pokemon/type/new', methods=['GET', 'POST'])
@login_required
def new_type():
  if request.method == 'POST':
    name = request.form.get('name')
    type = db.session.scalar(db.select(PokemonType).where(PokemonType.name == name))
    if type:
      flash('Pokemon Type already exists!', 'warning')
    else:
      # type = PokemonType(name=name, user=current_user)
      type = PokemonType(name=name, user_id=current_user.id)
      db.session.add(type)
      db.session.commit()
      flash('Add New Pokemon Type Successful.', 'success')
      return redirect(url_for('pokemon_types'))
  
  return render_template('type/new_type.html',
                         title='New Car Model Page')

@app.route('/pokemon/type/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update_type(id):
  type = db.session.get(PokemonType, id)
  if request.method == 'POST':
    name = request.form.get('name')
    pokemon_type = db.session.scalar(db.select(PokemonType).where(PokemonType.name == name))
    if pokemon_type:
      flash('Car Model already exists!', 'warning')
    else:
      # type = PokemonType(name=name, user=current_user)
      type.name = name
      type.user = current_user
      # type.user_id = current_user.id
      db.session.commit()
      flash('Update Car Model Successful.', 'success')
      return redirect(url_for('pokemon_types'))
  
  return render_template('type/update_type.html',
                         title='Update Car Model Page',
                       type=type)

@app.route('/pokemon/pokedex', methods=['GET', 'POST'])
@login_required
def pokedex():
    # Check if there is a search query (using POST)
    search_query = request.form.get('pokemon_name') if request.method == 'POST' else None

    # If there is a search query, filter the pokemons based on the name
    if search_query:
        pokemons = db.session.scalars(
            db.select(Pokemon).where(Pokemon.name.ilike(f'%{search_query}%'))
        ).all()
    else:
        # If no search query, return all pokemons
        pokemons = db.session.scalars(db.select(Pokemon)).all()

    return render_template('pokemon/index.html',
                           title='Car Page',
                           pokemons=pokemons,
                           search_query=search_query)

@app.route('/pokemon/pokedex/new_pokemon', methods=['GET', 'POST'])
@login_required
def new_pokemon():
  types = db.session.scalars(db.select(PokemonType)).all()
  if request.method == 'POST':
    name = request.form.get('name')
    weight = request.form.get('weight')
    height = request.form.get('height')
    description = request.form.get('description')
    img_url = request.form.get('img_url')
    pokemon_types = request.form.getlist('pokemon_types')

    pokemon = db.session.scalar(db.select(Pokemon).where(
      Pokemon.name == name))
    if pokemon:
      flash('Pokemon is already exists!', 'warning')
    else:

      p_types = []
      for id in pokemon_types:
        p_types.append(db.session.get(PokemonType, id))
      
      pokemon = Pokemon(name=name, 
                        weight=weight,
                        height=height,
                        description=description,
                        img_url=img_url,
                        user=current_user,
                        types=p_types)
      db.session.add(pokemon)
      db.session.commit()
      flash('Add new pokemon successful!', 'success')
      return redirect(url_for('pokedex'))
  
  return render_template('pokemon/new_pokemon.html',
                         title='New Car Page',
                         types=types)

@app.route('/pokemon/pokedex/<int:id>/detail')
@login_required
def detail_pokemon(id):
  pokemon = db.session.get(Pokemon, id)
  return render_template('pokemon/detail_pokemon.html',
                         title='Car\'s Detail Page',
                         pokemon=pokemon)

@app.route('/delete_pokemon/<int:id>', methods=['GET'])
def delete_pokemon(id):
    pokemon = Pokemon.query.get(id)
    if pokedex:
      db.session.delete(pokemon)
      db.session.commit()
      flash('Car deleted successfully!', 'success')
    else:
      flash('Car not found!', 'danger')
    
    # Redirect to the Pokémon list page ('pokedex') after deletion
    return redirect(url_for('pokedex'))

@app.route('/delete_type/<int:id>', methods=['GET'])
@login_required
def delete_type(id):
    pokemon_type = PokemonType.query.get(id)
    if pokemon_type:
        db.session.delete(pokemon_type)
        db.session.commit()
        flash('Car Model deleted successfully!', 'success')
    else:
        flash('Car Model not found!', 'danger')
    
    return redirect(url_for('pokemon_types'))
