from OpenGL.GL import *
import numpy

import entity
import model
import bullets
import particle

class Alien1(entity.Entity):
    """The first alien enemy. Slow. Shoots at the player every once in a
    while"""

    model = None

    # This alien's starting health
    health = 3

    def __init__(self, target):

        if Alien1.model is None:
            # Initialize the model for this ship
            Alien1.model = model.ObjModel("alien_torus.obj", scale=10)

        super(Alien1, self).__init__(Alien1.model, 20)

        # This is who we're shooting at
        self.player = target

        self.health = Alien1.health

        # Choose a position to spawn
        self.pos = numpy.array([0,0,0],dtype=float)

        # Rotation around its axis, this simply increases with time
        self.rot = 0

        # its velocity
        self.vel = numpy.zeros((3,))

        # When this countdown reaches 0, the alien ship will re-direct itself
        # towards the player
        self.redirect_countdown = 100

        self.bullet_countdown = 80

        self.bullets = bullets.Bullets(color=(1,0,0,1))

    def damage(self, amt):
        """Damages the alien.
        Returns True if the alien is destroyed.
        """
        self.health -= amt
        if self.health <= 0:
            particle.explosion(self.pos, (10,0,0), self.vel)
            return True
        return False

    def update(self):
        self.bullets.update()

        self.rot += 5
        if self.rot >= 360:
            self.rot -= 360

        self.pos += self.vel

        self.redirect_countdown -= 1
        self.bullet_countdown -= 1

        # Gradually slow down our speed
        self.vel *= 0.995

        if self.redirect_countdown <= 0:
            self.redirect_countdown = 200

            newdir = self.player.pos - self.pos
            # normalize to a constant speed
            newdir /= numpy.linalg.norm(newdir)
            newdir *= 3

            self.vel = newdir

        if self.bullet_countdown <= 0:
            # Fire a bullet towards the player
            self.bullet_countdown = 80

            bulvel = self.player.pos - self.pos
            # normalize to a constant speed
            bulvel /= numpy.linalg.norm(bulvel)
            bulvel *= self.bullets.speed

            self.bullets.fire(self.pos, bulvel)




    def draw(self):
        glPushMatrix()

        # Translate to the right pos
        glTranslated(*self.pos)

        # Rotate slightly for a better view
        #glRotated(20, 1, 0, 0)

        # The turning rotations
        glRotated(self.rot, 0, 1, 0)

        # Finally, draw the thing
        self.model.draw()

        glPopMatrix()

        self.bullets.draw()
